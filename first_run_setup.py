import json
import sys
import webbrowser
from live_settings import LiveSettings
import locale
import logging
from os import PathLike
import os.path
import socket
import re


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


def _get_channel_from_answer(answer: str) -> str:
    match = re.search(r'\d+ (\S+) :', answer)
    return match.group(1) if match else ''


def _validate_token_get_channel(token: str, settings: LiveSettings) -> (bool, str):
    token = f'oauth:{token}'
    nickname = 'test'
    channel = ''
    try:
        soc = socket.socket()
        soc.settimeout(10)
        soc.connect((TWITCH_SERVER, TWITCH_PORT))
        soc.send(f'PASS {token}\n'.encode('utf-8'))
        soc.send(f'NICK {nickname}\n'.encode('utf-8'))
        soc.send(f'JOIN #{channel}\n'.encode('utf-8'))
        answer = soc.recv(2048).decode('utf-8')
        if 'Login authentication failed' in answer:
            print(settings.translate_param('get_token_invalid'), file=sys.stderr)
        if '001' in answer:
            print(settings.translate_param('get_token_success'))
            channel = _get_channel_from_answer(answer)
            return True, channel
    except TimeoutError:
        print(settings.translate_param('get_token_timeout'), file=sys.stderr)
    except socket.gaierror:
        print(settings.translate_param('get_token_gai_error'), file=sys.stderr)

    return False, ''


def _get_token_and_channel(settings: LiveSettings) -> (str, str):
    while True:
        print(settings.translate_param('get_token'), end='', flush=True)
        token = input()
        valid, channel = _validate_token_get_channel(token, settings)
        if valid:
            break
    return token, channel


def _is_valid_name(name: str) -> bool:
    if name.isascii() and name.replace('_', '').isalpha():
        return True
    return False


def _get_nickname(settings: LiveSettings) -> str:
    while True:
        nickname = input(settings.translate_param('get_nickname'))
        if _is_valid_name(nickname):
            return nickname.lower()
        print(settings.translate_param('get_nickname_error').format(nickname), file=sys.stderr)


def _get_channel(settings: LiveSettings, default_channel: str) -> str:
    while True:
        channel = input(settings.translate_param('get_channel').format(default_channel))
        if not channel:
            return default_channel
        if _is_valid_name(channel):
            return channel.lower()
        print(settings.translate_param('get_channel_error').format(channel), file=sys.stderr)


def fist_run_setup(settings: LiveSettings, tokens_fn: PathLike | str) -> None:
    if os.path.isfile(tokens_fn):
        return
    _locale_setup(settings)
    _token_sites_example(settings)
    _check_twitch_server_access(settings)
    token, channel = _get_token_and_channel(settings)
    nickname = _get_nickname(settings)
    _write_json(tokens_fn, nickname, token)
    settings.twitch_channel = _get_channel(settings, channel)

