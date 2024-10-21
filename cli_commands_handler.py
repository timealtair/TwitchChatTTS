from ai_streamer_lib import ConsoleAutoCompleter
from live_settings import LiveSettings


class CliCommandsHandler(ConsoleAutoCompleter):
    """
    Run in separate thread, locks forever in input loop.
    1st arg = settings
    """
    def __init__(self, settings: LiveSettings):
        cmds = [settings.translate_param(cmd) for cmd in settings.get_names()]
        ConsoleAutoCompleter.__init__(self, cmds)

        self.run()
