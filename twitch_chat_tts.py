import asyncio
import threading

from ai_streamer_lib import twitch_chat_reader
from gtts_realtime import speak_text


async def read_chat_loop(reader, settings):
    while not settings.twitch_disable:
        if not reader:
            await asyncio.sleep(0.1)
            continue

        if settings.twitch_read_firsts:
            usr, msg = reader.get_message_from_left_end()
        else:
            usr, msg = reader.get_message_from_right_end()

        txt = settings.concatenate_func(usr, msg)
        if not txt:
            await asyncio.sleep(0.1)
            continue

        await speak_text(txt, settings.tts_lang)
        await asyncio.sleep(settings.tts_min_pause)


if __name__ == '__main__':
    class CustomSetting:
        def __init__(self):
            self.twitch_read_firsts = False
            self.twitch_print_messages = True
            self.twitch_should_filter = False
            self.twitch_remove_censored = False
            self.twitch_channel = 'stariy_bog'
            self.twitch_censore_by = '*'
            self.twitch_replace_ban_word_dict = None
            self.twitch_disable = False

            self.tts_min_pause = 2
            self.tts_lang = 'ru'
            self.concatenate_func = lambda usr, msg: f'{msg}'

    settings = CustomSetting()

    tokens_file = 'tokens.json'
    stop_event = threading.Event()
    threads = []
    reader = twitch_chat_reader.TwitchChatReader(tokens_file, settings, stop_event, threads)

    try:
        asyncio.run(read_chat_loop(reader, settings))
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
