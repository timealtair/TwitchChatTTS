import readline


class ConsoleAutoCompleter:
    """
    Usage example:

    class CustomConsoleApplication(ConsoleAutoCompleter):
        def __init__(self):
            super().__init__(['start', '...'])

        def execute_command(self, command):
            if command == 'start':
                print('Starting...')
            elif command == '...':
                self.print_all_commands()
            else:
                print('Unknown command')

        def run(self):
            super().run()
    """

    def __init__(self, commands=None, prompt='> '):
        self.commands = commands if commands else []
        self.prompt = prompt

    def run(self):
        while True:
            user_input = self.get_input()
            if user_input:
                self.execute_command(user_input)

    def get_input(self):
        readline.set_completer(self.autocomplete)
        readline.parse_and_bind('tab: complete')
        try:
            user_input = input(self.prompt)
        except Exception:
            raise SystemExit
        return user_input

    def autocomplete(self, text, state):
        options = [cmd for cmd in self.commands if cmd.startswith(text) or text in cmd]
        if state <= len(options):
            return options[state]
        else:
            return None

    def execute_command(self, command):
        # To be implemented by subclass
        pass

    def print_all_commands(self, prefix=''):
        for command in self.commands:
            if command.startswith(prefix):
                print(command)


if __name__ == '__main__':
    app = CustomConsoleApplication()
    app.run()
