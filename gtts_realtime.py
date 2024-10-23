import time
from gtts import gTTS
import io
import logging
import asyncio
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

pygame.mixer.init()


async def speak_text(text, lang='ru'):
    try:
        mp3_fp = io.BytesIO()

        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(mp3_fp)

        mp3_fp.seek(0)

        pygame.mixer.music.load(mp3_fp)

        logging.debug('volume=%r', pygame.mixer.music.get_volume())

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            logging.debug('sleeping')
            await asyncio.sleep(0.1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def stop_speak():
    pygame.mixer.music.stop()


async def main():
    logging.basicConfig(level=logging.WARN)

    print("Enter the text you want to convert to speech (in Russian):")
    while True:
        user_input = input("Text: ")

        await speak_text(user_input)


if __name__ == "__main__":
    asyncio.run(main())
