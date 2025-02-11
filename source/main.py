import asyncio
import sys
import threading
import logging
import locale
from twitch_chat_reader import TwitchChatReader
from gtts_realtime import (
    speak_text, stop_speak, get_locales, generate_speech, play_speech
)
from live_settings import LiveSettings
from cli_commands_handler import CliCommandsHandler
from first_run_setup import fist_run_setup
from concurrent.futures import ThreadPoolExecutor


async def read_chat_loop(reader, settings, stop_event):
    while not stop_event.is_set():
        if settings.twitch_disable or not reader:
            await asyncio.sleep(1)
            continue

        if settings.twitch_read_firsts:
            usr, msg = reader.get_message_from_left_end()
        else:
            usr, msg = reader.get_message_from_right_end()

        txt = settings._concatenate_func(usr, msg)
        if not txt:
            await asyncio.sleep(0.1)
            continue

        if settings.twitch_print_messages:
            print(f'{usr}: {msg}')
        if settings.tts_voice_nicknames:
            futures_list = []
            with ThreadPoolExecutor() as executor:
                futures_list.append(
                    executor.submit(generate_speech, usr, lang='en')
                )
                futures_list.append(
                    executor.submit(generate_speech, txt, lang=settings.tts_lang)
                )
            for future in futures_list:
                try:
                    await play_speech(future.result())
                except AssertionError:
                    break
        else:
            try:
                await speak_text(txt, settings.tts_lang)
            except AssertionError:
                break
        await asyncio.sleep(settings.tts_min_pause)


if __name__ == '__main__':
    stop_event = threading.Event()
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        logging.basicConfig(level=logging.CRITICAL)

        tokens_file = 'tokens.json'
        locale_json_fn = 'locales.json'
        settings_fn = 'settings.json'
        bans_fn = 'banned_users.yml'

        settings = LiveSettings(locale_json_fn, settings_fn, bans_fn)
        settings.load_settings_from_file()
        fist_run_setup(settings, tokens_file, get_locales)
        threads = []
        reader = TwitchChatReader(tokens_file, settings, stop_event, threads)
        threading.Thread(target=CliCommandsHandler, args=(settings, stop_event,
                                                          reader.clear_all,
                                                          stop_speak,
                                                          tokens_file,
                                                          get_locales)).start()

        asyncio.run(read_chat_loop(reader, settings, stop_event))
    except (KeyboardInterrupt, EOFError, SystemExit):
        pass
    except Exception as e:
        print('Unexpected error while running: %s' % e, file=sys.stderr)
        input('Press "ENTER" to exit: ')
    finally:
        stop_event.set()
