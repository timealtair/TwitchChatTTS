import sys
from pprint import pprint
from threading import Event
from ai_streamer_lib import ConsoleAutoCompleter
from live_settings import LiveSettings
from typing import Callable


class CliCommandsHandler(ConsoleAutoCompleter):
    """
    Run in separate thread, locks forever in input loop.
    1st arg = settings
    """
    def __init__(self, settings: LiveSettings, stop_event: Event, clear_chat_func: Callable):
        self._settings = settings
        self._stop_event = stop_event
        self._clear_chat_func = clear_chat_func

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

    @staticmethod
    def unknown_cmd_print(cmd) -> None:
        print(f'>>> {cmd} ???', file=sys.stderr)

    def help_text_print(self, help_for) -> None:
        help_for = self._settings.translate_param(help_for)
        print(self._settings.translate_param(f'help_{help_for}'))

    def clear_twitch_messages(self):
        self._clear_chat_func()

    def extended_cmds_handle(self, cmd: str, args: str) -> None:
        match cmd:
            case 'exit':
                self._stop_event.set()
                raise SystemExit
            case 'help':
                help_for = args if args else cmd
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
            case _:
                self.unknown_cmd_print(cmd)

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
            self.extended_cmds_handle(cmd, args)

    def welcome_print(self):
        msg = self._settings.translate_param('welcome')
        msg = msg.format(self._settings.twitch_channel, self._settings.tts_lang,
                         self._settings.tts_min_pause, self._settings.cli_locale)
        print(msg)
