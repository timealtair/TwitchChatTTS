from live_settings import LiveSettings
import logging
from logging import Logger


def _get_current_log_lvl_name(log: Logger) -> str:
    lvl_int = log.getEffectiveLevel()
    return logging.getLevelName(lvl_int).lower()


def logging_level_changer(settings: LiveSettings) -> None:
    log = logging.getLogger()
    lvl = _get_current_log_lvl_name(log)
    choice = input(settings.translate_param('logging_setup_info').format(lvl))
    match choice:
        case '':
            print(settings.translate_param('logging_setup_cancel'))
        case '1':
            log.setLevel(logging.DEBUG)
        case '2':
            log.setLevel(logging.INFO)
        case '3':
            log.setLevel(logging.WARNING)
        case '4':
            log.setLevel(logging.ERROR)
        case '5':
            log.setLevel(logging.CRITICAL)
        case _:
            print(settings.translate_param('logging_setup_cancel'))
    lvl = _get_current_log_lvl_name(log)
    print(settings.translate_param('logging_setup_result').format(lvl))
