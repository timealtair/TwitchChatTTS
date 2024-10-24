import os.path
import sys
import shutil
from pprint import pprint
from threading import Event
from console_auto_completer import ConsoleAutoCompleter
from live_settings import LiveSettings
from typing import Callable
from os import PathLike
from datetime import datetime
from first_run_setup import fist_run_setup


class CliCommandsHandler(ConsoleAutoCompleter):
    """
    Run in separate thread, locks forever in input loop.
    1st arg = settings
    """
    def __init__(self, settings: LiveSettings, stop_event: Event,
                 clear_chat_func: Callable, stop_tts_func: Callable,
                 _tokens_file: PathLike | str, get_locales_func: Callable):
        self._settings = settings
        self._stop_event = stop_event
        self._clear_chat_func = clear_chat_func
        self._stop_tts_func = stop_tts_func
        self._tokens_file = _tokens_file
        self._get_locales_func = get_locales_func

        cmds = self._settings._ext_commands + settings.get_names()
        cmds = [settings.translate_param(cmd) for cmd in cmds]

        self.welcome_print()

        ConsoleAutoCompleter.__init__(self, cmds)
        self.run()

    def parse_cmd_args(self, cmd: str) -> (str, str):
        """
        :param cmd: raw input in user's locale
        :return: cmd, args
        """
        cmd, *args = cmd.split()
        cmd = self._settings.translate_param(cmd.lower())
        args = ' '.join(args).lower().strip('\'"')
        return cmd, args

    def unknown_cmd_print(self, cmd: str) -> None:
        print(self._settings.translate_param('unknown_command').format(cmd), file=sys.stderr)

    def help_text_print(self, help_for) -> None:
        help_for = self._settings.translate_param(help_for)
        print(self._settings.translate_param(f'help_{help_for}'))

    def clear_twitch_messages(self):
        self._clear_chat_func()

    def move_tokens_file_to_backup(self):
        dir_name = 'backups'
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        file_name, ext = os.path.splitext(self._tokens_file)
        current_time = datetime.now().strftime("%Y_%m_%d__%H_%M_%S_%f")[:-4]
        backup_file_name = f'{file_name}_backup__{current_time}{ext}'
        dist = os.path.join(dir_name, backup_file_name)
        shutil.move(self._tokens_file, dist)

    def quick_setup(self) -> None:
        answer = input(self._settings.translate_param('quick_setup_warn')).lower()
        if answer == 'y' or answer == 'yes':
            self.move_tokens_file_to_backup()
            fist_run_setup(self._settings, self._tokens_file, self._get_locales_func)

    def extended_cmds_handle(self, cmd: str, args: str, raw_cmd: str) -> None:
        match cmd:
            case 'exit':
                self._stop_event.set()
                raise SystemExit
            case 'help':
                help_for = args if args else self._settings.translate_param(cmd)
                self.help_text_print(help_for)
            case 'ban':
                self._settings.ban_username(args)
            case 'unban':
                if not self._settings.unban_username(args):
                    self.help_text_print(cmd)
            case 'banned':
                pprint(self._settings.get_banned_usernames())
            case 'vals':
                pprint({self._settings.translate_param(key): val
                        for key, val in self._settings.get_values().items()})
            case 'reset':
                self._settings.reset_settings()
            case 'clear':
                self.clear_twitch_messages()
            case 'cli_locales':
                pprint(self._settings.get_supported_cli_locales())
            case 'skip':
                self._stop_tts_func()
            case 'quick_setup':
                self.quick_setup()
            case 'tts_langs':
                pprint(self._get_locales_func())
            case _:
                self.unknown_cmd_print(raw_cmd)

    def execute_command(self, command):
        cmd, args = self.parse_cmd_args(command)
        if cmd.startswith('_'):
            pass
        elif cmd in self._settings:
            if args:
                self._settings[cmd] = self._settings.convert_type_string(args)
                self._settings.save_settings_to_file()
            else:
                pprint(self._settings[cmd])
        else:
            self.extended_cmds_handle(cmd, args, command)

    def welcome_print(self):
        msg = self._settings.translate_param('welcome')
        msg = msg.format(self._settings.twitch_channel, self._settings.tts_lang,
                         self._settings.tts_min_pause, self._settings.cli_locale)
        print(msg)
