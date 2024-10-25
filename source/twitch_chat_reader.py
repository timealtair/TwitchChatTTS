import json
import re
import socket
import time
import threading
# import queue
from collections import deque
import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from censorer import Censorer
from live_settings import LiveSettings as Settings


class TwitchChatReader:

    def __init__(self, file_with_tokens, settings,
                 stop_event, thread_list_for_append, blocking_time=1):
        self.__nickname = None
        self.__token = None
        self.__channel = None
        self.__connected_to_channel = None
        self.__server = None
        self.__port = None
        self.__sock = None
        self.__blocking_time = blocking_time
        self.__stop_event = stop_event
        self.__settings: Settings = settings

        self.__load_settings(file_with_tokens)

        self.__chat_deque = deque()

        self.__re_compile = re.compile(r'^.*:(\S+)!.*?:(.*)$', re.MULTILINE)

        reader_thread = threading.Thread(target=self.__read_messages)
        reader_thread.start()
        thread_list_for_append.append(reader_thread)

    def __load_settings(self, file_with_tokens):
        with open(file_with_tokens, 'r') as file:
            credentials = json.load(file)
        self.__nickname = credentials['nickname']
        self.__channel = credentials['channel']
        self.__token = credentials['token']
        self.__server = credentials['server']
        self.__port = credentials['port']

    def __connect(self):
        if self.__settings.twitch_channel is None:
            self.__connected_to_channel = self.__channel
        else:
            self.__connected_to_channel = self.__settings.twitch_channel

        self.__sock = socket.socket()
        self.__sock.connect((self.__server, self.__port))
        self.__sock.settimeout(self.__blocking_time)
        self.__sock.send(f"PASS {self.__token}\n".encode('utf-8'))
        self.__sock.send(f"NICK {self.__nickname}\n".encode('utf-8'))
        self.__sock.send(f"JOIN #{self.__connected_to_channel}\n".encode('utf-8'))

    def __disconnect(self):
        if self.__sock is not None:
            self.__sock.shutdown(socket.SHUT_RDWR)
            self.__sock.close()
            self.__sock = None

    def change_channel(self, channel: str):
        self.__settings.twitch_channel = channel

    def __handle_channel_change(self):
        if self.__settings.twitch_channel is None:
            if self.__channel == self.__connected_to_channel:
                return
        if self.__connected_to_channel == self.__settings.twitch_channel:
            return
        self.__disconnect()
        self.__connect()
        self.clear_all()

    def __len__(self):
        return len(self.__chat_deque)

    def __iter__(self):
        return self

    def __bool__(self):
        return bool(len(self))

    def __next__(self):
        if self:
            if self.__settings.twitch_read_firsts:
                return self.get_message_from_left_end()
            else:
                return self.get_message_from_right_end()
        else:
            raise StopIteration

    def is_empty(self):
        return not len(self)

    def get_message_from_right_end(self):
        return self.__chat_deque.pop()

    def get_message_from_left_end(self):
        return self.__chat_deque.popleft()

    def append_message(self, message):
        self.__chat_deque.append(message)

    def insert_message(self, message):
        self.__chat_deque.appendleft(message)

    def clear_all(self):
        self.__chat_deque = deque()
        
    def __clean_message_iter(self, message):
        logging.debug('entering __clean_message_iter')
        find_iter = self.__re_compile.finditer(message)
        for match in find_iter:
            logging.debug('match=%r', match)
            groups = match.groups()
            logging.debug('groups=%r', groups)
            yield groups
        yield '', ''

    def __read_messages(self):
        if self.__settings.twitch_should_filter:
            censorer: Censorer = Censorer(self.__settings._twitch_replace_ban_word_dict)

        empty_messages_occurrences = 0
        while not self.__stop_event.is_set():
            if self.__settings.twitch_disable:
                self.__disconnect()
                time.sleep(2)
                continue

            if self.__sock is None:
                try:
                    self.__connect()
                except socket.gaierror:
                    logging.error('Can\'t connect to twitch chat.',
                                  'Retrying in 2 secs...')
                    self.__sock = None
                    time.sleep(2)
                    continue

            try:
                self.__handle_channel_change()
                resp = self.__sock.recv(2048).decode('utf-8')
            except TimeoutError:
                continue
            except OSError:
                logging.error('Can\'t receive message from twitch chat.',
                              'Retrying in 2 secs')
                time.sleep(2)
                continue

            logging.debug('raw=%r', resp)
            clean = self.__clean_message_iter(resp)
            logging.debug('clean=%r', clean)
            if not clean:
                time.sleep(0.1)
                logging.debug('sleeping')
                continue

            for user, cleaned_message in clean:
                if not user:
                    logging.warning('empty user')
                    if empty_messages_occurrences < 10:
                        empty_messages_occurrences += 1
                        time.sleep(0.1)
                        continue
                    empty_messages_occurrences = 0
                    logging.warning('empty user 10 time, reconnecting')
                    self.__disconnect()
                    self.__connect()
                    time.sleep(0.1)
                logging.debug('user=%r, cleaned_message=%r', user, cleaned_message)

                if self.__settings.twitch_should_filter:
                    # noinspection PyUnboundLocalVariable
                    cleaned_message = (censorer.
                                       censor_it(cleaned_message,
                                                 self.__settings.twitch_remove_censored,
                                                 self.__settings.twitch_censore_by))

                if cleaned_message:
                    self.append_message((user, cleaned_message))
                    if self.__settings.twitch_print_messages:
                        logging.info('%r: %r', user, cleaned_message)
                else:
                    logging.warn('filtered or empty msg, raw=%r', resp)
                    time.sleep(0.1)


if __name__ == '__main__':
    class CustomSetting:
        def __init__(self):
            self.twitch_read_firsts = True
            self.twitch_print_messages = True
            self.twitch_should_filter = False
            self.twitch_remove_censored = False
            self.twitch_channel = 'vedal987'
            self.twitch_censore_by = '*'
            self.twitch_replace_ban_word_dict = None
            self.twitch_disable = False

    settings = CustomSetting()

    logging.basicConfig(level=logging.WARN)
    tokens_file = 'tokens.json'
    stop_event = threading.Event()
    threads = []
    reader = TwitchChatReader(tokens_file, settings, stop_event, threads)

    try:
        while True:
            for usr, msg in reader:
                print(f'{usr}: {msg}')

            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
