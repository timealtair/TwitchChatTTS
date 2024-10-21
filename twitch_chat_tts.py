import asyncio
import re
import threading
import logging

from ai_streamer_lib import TwitchChatReader
from ai_streamer_lib import BaseSettings
from gtts_realtime import speak_text


# OopCompanion:suppressRename


async def read_chat_loop(reader, settings, stop_event):
    while not stop_event.is_set():
        if settings.twitch_disable or not reader:
            await asyncio.sleep(1)
            continue

        if settings.twitch_read_firsts:
            usr, msg = reader.get_message_from_left_end()
        else:
            usr, msg = reader.get_message_from_right_end()

        txt = settings._concatenate_func(usr, msg)
        if not txt:
            await asyncio.sleep(0.1)
            continue

        await speak_text(txt, settings.tts_lang)
        await asyncio.sleep(settings.tts_min_pause)


class LiveSettings(BaseSettings):
    def __init__(self):
        self.twitch_read_firsts = False
        self.twitch_print_messages = True
        self.twitch_should_filter = False
        self.twitch_remove_censored = False
        self.twitch_channel = 'betboom_ru'
        self.twitch_censore_by = '*'
        self.twitch_replace_ban_word_dict = None
        self.twitch_disable = False

        self.tts_min_pause = 2
        self.tts_lang = 'ru'
        self._concatenate_func = self.clean_msg
        self.replace_links_with = 'link'
        self.skip_answers = False

        self._banned_users = {'nightbot'}

    def ban_username(self, username):
        self._banned_users.add(username)

    def unban_username(self, username):
        self._banned_users.remove(username)

    def get_banned_usernames(self):
        return ', '.join(self._banned_users)

    def remove_links(self, text: str) -> str:
        pattern = r'http(\S+)'
        return re.sub(pattern, self.replace_links_with, text)

    @staticmethod
    def remove_repeat_words(text: str) -> str:
        words = text.split()
        res = []
        last_word = ''
        for word in words:
            if word != last_word:
                res.append(word)
            last_word = word
        return ' '.join(res)

    def clean_msg(self, usr: str, msg: str) -> str:
        if usr in self._banned_users or msg.startswith('!'):
            return ''
        streamer = '@' + self.twitch_channel
        if streamer in msg:
            msg = msg.replace(streamer, '')
        if '@' in msg:
            if self.skip_answers:
                return ''
            else:
                msg = re.sub(r'@\w+', '', msg)
        msg = self.remove_repeat_words(msg)
        msg = self.remove_links(msg)
        return msg


if __name__ == '__main__':

    settings = LiveSettings()

    tokens_file = 'tokens.json'
    stop_event = threading.Event()
    threads = []
    reader = TwitchChatReader(tokens_file, settings, stop_event, threads)

    try:
        asyncio.run(read_chat_loop(reader, settings, stop_event))
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
