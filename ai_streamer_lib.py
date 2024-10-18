import sys

AI_STREAMER_LIB_DIR = r'D:\llmcreat\tts\code'

sys.path.append(AI_STREAMER_LIB_DIR)

import twitch_chat_reader


if __name__ == '__main__':
    print(dir(twitch_chat_reader))
