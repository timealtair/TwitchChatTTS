import asyncio
import threading
import logging

from ai_streamer_lib import TwitchChatReader
from gtts_realtime import speak_text
from live_settings import LiveSettings


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

        await speak_text(txt, settings.tts_lang)
        await asyncio.sleep(settings.tts_min_pause)


if __name__ == '__main__':
    settings = LiveSettings()

    tokens_file = 'tokens.json'
    stop_event = threading.Event()
    threads = []
    reader = TwitchChatReader(tokens_file, settings, stop_event, threads)

    try:
        asyncio.run(read_chat_loop(reader, settings, stop_event))
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
