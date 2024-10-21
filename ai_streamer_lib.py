import sys

AI_STREAMER_LIB_DIR = r'D:\llmcreat\tts\code'

sys.path.append(AI_STREAMER_LIB_DIR)

from twitch_chat_reader import TwitchChatReader
from base_settings import BaseSettings
from console_auto_completer import ConsoleAutoCompleter


if __name__ == '__main__':
    print(dir(TwitchChatReader))
    print(dir(BaseSettings))
    print(dir(ConsoleAutoCompleter))
