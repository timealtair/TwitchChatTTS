from ai_streamer_lib import BaseSettings
import re
import json


class LiveSettings(BaseSettings):
    def __init__(self, locale_json_fn):
        self.twitch_read_firsts = False
        self.twitch_print_messages = True
        self.twitch_should_filter = False
        self.twitch_remove_censored = False
        self.twitch_channel = 'betboom_ru'
        self.twitch_censore_by = '*'
        self.twitch_disable = False

        self.tts_min_pause = 2
        self.tts_lang = 'ru'
        self.replace_links_with = 'link'
        self.skip_answers = False

        self.cli_locale = 'en'
        self.locale_dict = self.load_locales(locale_json_fn)

        self._twitch_replace_ban_word_dict = None
        self._banned_users = {'nightbot'}
        self._concatenate_func = self.clean_msg

    def ban_username(self, username) -> None:
        self._banned_users.add(username)

    def unban_username(self, username) -> None:
        self._banned_users.remove(username)

    def get_banned_usernames(self) -> str:
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

    @staticmethod
    def load_locales(json_fn) -> dict:
        res = {}
        with open(json_fn) as f:
            d = json.load(f)
        for locale in d:
            res[locale] = {}
            for k, v in d[locale]:
                res[locale][k] = v
                res[locale][v] = k
        return res

    def translate_param(self, param_name) -> str:
        locale_dict = self.locale_dict.get(self.cli_locale, 'en')
        return locale_dict[param_name]


