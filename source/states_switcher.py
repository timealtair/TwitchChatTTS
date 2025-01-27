from live_settings import LiveSettings


class StatesSwitcher:
    def __init__(self, settings: LiveSettings):
        self._settings = settings
        self._dialog_choice_text_key = 'state_parameter_choice'
        self._dialog_result_unchanged = "state_parameter_result_unchanged"
        self._dialog_result_value_set = "state_parameter_result_value_set"

    def _get_parameter_value(self, parameter_name: str):
        return getattr(self._settings, parameter_name)

    def switch_state_interface(self, parameter_name: str):
        print(self._settings.translate_param(f'help_{parameter_name}'))
        current_state = self._get_parameter_value(parameter_name)
        try:
            choice = input(
                self._settings.translate_param(self._dialog_choice_text_key)
                .format(current_state)
            )
        except (KeyboardInterrupt, EOFError):
            choice = ''
        if choice and choice.lower() in 'yes':
            setattr(self._settings, parameter_name, not current_state)
            self._settings.save_settings_to_file()
            new_state = self._get_parameter_value(parameter_name)
            print(
                self._settings.translate_param(self._dialog_result_value_set)
                .format(new_state)
            )
        else:
            print(self._settings.translate_param(self._dialog_result_unchanged))
