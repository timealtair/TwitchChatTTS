import json
import sys
import webbrowser
from live_settings import LiveSettings
import locale
import logging
from os import PathLike
import os.path
import socket


TOKENS_GEN_SITES = (r'https://twitchtokengenerator.com/?scope=chat:read&auth=auth_stay',)
TWITCH_SERVER = 'irc.chat.twitch.tv'
TWITCH_PORT = 6667


def _get_locale() -> str:
    return locale.getdefaultlocale()[0].split('_')[0]


def _write_json(tokens_fn: PathLike | str, nickname: str, token: str) -> None:
    nickname = nickname
    token = f'oauth:{token}'
    channel = ""
    server = TWITCH_SERVER
    port = TWITCH_PORT
    data = dict(nickname=nickname, token=token,
                channel=channel, server=server,
                port=port)
    with open(tokens_fn, 'w') as f:
        json.dump(data, f, indent=4)


def _locale_setup(settings: LiveSettings) -> None:
    lang = _get_locale()
    locales = settings.get_supported_cli_locales()
    settings.cli_locale = lang if lang in locales else 'en'
    logging.debug('locale=%r', settings.cli_locale)
    print(settings.translate_param("startup_lang").format(locales, settings.cli_locale),
          end='', flush=True)
    while True:
        lang = input()
        if not lang:
            break
        if lang in locales:
            settings.cli_locale = lang
            break
        print(settings.translate_param("startup_lang_error").format(lang,
                                                                    locales,
                                                                    settings.cli_locale),
              file=sys.stderr, end='', flush=True)


def _clickable_url(url: str) -> str:
    return f'\033[94m{url}\033[0m'


def _open_site(site_num: int) -> bool:
    idx = site_num - 1
    url = TOKENS_GEN_SITES[idx]
    try:
        return webbrowser.open(url)
    except webbrowser.Error:
        return False


def _token_sites_example(settings: LiveSettings) -> None:
    urls = '\n'.join((f'{i}: {_clickable_url(url)}' for i, url in enumerate(TOKENS_GEN_SITES, 1)))
    print(settings.translate_param('startup_token').format(urls))
    while True:
        print(settings.translate_param('startup_token_open'),  end='', flush=True)
        site = input()
        if not site or site == settings.translate_param('startup_no'):
            break
        try:
            site = int(site)
            if site in range(1, len(TOKENS_GEN_SITES)+1):
                if not _open_site(site):
                    print(settings.translate_param('startup_token_browser_error'), file=sys.stderr)
                break
        except ValueError:
            pass
        print(settings.translate_param('startup_token_open_error').format(site), file=sys.stderr)


def _check_twitch_server_access(settings: LiveSettings) -> None:
    host = TWITCH_SERVER
    port = TWITCH_PORT
    print(settings.translate_param('check_twitch_server'))
    while True:
        try:
            print(settings.translate_param('check_twitch_server_try'))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((host, port))
                print(settings.translate_param('check_twitch_server_success'))
                break
        except socket.error as e:
            print(settings.translate_param('check_twitch_server_failed'), file=sys.stderr)
            input()


def _get_token(settings: LiveSettings) -> str:
    print(settings.translate_param('get_token'),  end='', flush=True)
    while True:
        token = input()
    pass


def fist_run_setup(settings: LiveSettings, tokens_fn: PathLike | str) -> None:
    if os.path.isfile(tokens_fn):
        return
    _locale_setup(settings)
    _token_sites_example(settings)
    _check_twitch_server_access(settings)
    token = _get_token(settings)

