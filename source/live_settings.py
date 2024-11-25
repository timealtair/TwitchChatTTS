import logging

from base_settings import BaseSettings
import re
import json
import yaml
from remove_repeats import remove_repeats


class LiveSettings(BaseSettings):
    def __init__(self, locale_json_fn, save_file: str, bans_file: str):
        self.twitch_read_firsts = True
        self.twitch_print_messages = True
        self.twitch_should_filter = False
        self.twitch_remove_censored = False
        self.twitch_channel = ''
        self.twitch_censore_by = '*'
        self.twitch_disable = False

        self.tts_min_pause = 5
        self.tts_lang = 'ru'
        self.replace_links_with = 'link'
        self.skip_answers = False

        self.cli_locale = 'en'
        self._locale_dict = self.load_locales(locale_json_fn)

        self._locale_json_fn = locale_json_fn
        self._twitch_replace_ban_word_dict = None
        self._banned_users = {'nightbot'}
        self._concatenate_func = self.clean_msg
        self._ext_commands = ['exit', 'help', 'ban', 'unban', 'banned', 'vals', 'reset', 'tts_langs',
                              'clear', 'cli_locales', 'quick_setup', 'skip', 'true', 'false']
        self._save_file = save_file
        self._bans_file = bans_file
        self._load_commands_func = None

    def save_settings_to_file(self):
        BaseSettings.save_settings_to_file(self, self._save_file)
        data = yaml.safe_dump(self._banned_users)
        with open(self._bans_file, 'w') as f:
            f.write(data)
        if self._load_commands_func:
            self._load_commands_func()

    def load_settings_from_file(self):
        BaseSettings.load_settings_from_file(self, self._save_file)
        try:
            with open(self._bans_file) as f:
                data = yaml.safe_load(f)
            self._banned_users = set(data)
        except FileNotFoundError:
            pass

    def ban_username(self, username) -> None:
        self._banned_users.add(username)
        self.save_settings_to_file()

    def unban_username(self, username) -> bool:
        try:
            self._banned_users.remove(username)
            self.save_settings_to_file()
            return True
        except KeyError:
            return False

    def get_banned_usernames(self) -> set:
        return self._banned_users

    def remove_links(self, text: str) -> str:
        pattern = r'http(\S+)'
        return re.sub(pattern, self.replace_links_with, text)

    @staticmethod
    def remove_repeat_words(text: str) -> str:
        return remove_repeats(text)

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
        logging.debug('msg: %r', msg)
        if not msg.strip():
            return ''
        msg = self.remove_repeat_words(msg)
        msg = self.remove_links(msg)
        return msg

    @staticmethod
    def load_locales(json_fn) -> dict:
        res = {}
        with open(json_fn, encoding='utf-8') as f:
            d = json.load(f)
        for locale in d:
            res[locale] = {}
            for k, v in d[locale].items():
                res[locale][k] = v
                res[locale][v] = k
        return res

    def translate_param(self, param_name) -> str:
        try:
            return self._locale_dict[self.cli_locale][param_name]
        except KeyError:
            return param_name

    def reset_settings(self):
        channel = self.twitch_channel
        self.__init__(self._locale_json_fn, self._save_file, self._bans_file)
        self.twitch_channel = channel
        BaseSettings.save_settings_to_file(self._save_file)
        self.load_settings_from_file()

    def get_supported_cli_locales(self) -> list:
        return list(self._locale_dict.keys())
