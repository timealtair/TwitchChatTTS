import time
from gtts import gTTS
from gtts.lang import tts_langs
import io
from io import BytesIO
import logging
import asyncio
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

pygame.mixer.init()


def generate_speech(text: str, lang: str) -> BytesIO:
    mp3_fp = io.BytesIO()

    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(mp3_fp)

    mp3_fp.seek(0)
    return mp3_fp


async def play_speech(mp3_fp: BytesIO) -> None:
    pygame.mixer.music.load(mp3_fp)

    logging.debug('volume=%r', pygame.mixer.music.get_volume())

    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        logging.debug('sleeping')
        await asyncio.sleep(0.1)


async def speak_text(text, lang='en') -> None:
    mp3_fp = generate_speech(text, lang)
    await play_speech(mp3_fp)


def stop_speak() -> None:
    pygame.mixer.music.stop()


def get_locales() -> dict:
    return tts_langs()


async def main():
    logging.basicConfig(level=logging.WARN)

    print("Enter the text you want to convert to speech:")
    while True:
        user_input = input("Text: ")

        await speak_text(user_input)


if __name__ == "__main__":
    asyncio.run(main())
