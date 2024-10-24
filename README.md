# TwitchChatTTS

![GitHub License](https://img.shields.io/github/license/timealtair/TwitchChatTTS)
![GitHub top language](https://img.shields.io/github/languages/top/timealtair/TwitchChatTTS)
![Static Badge](https://img.shields.io/badge/platform-windows-brightgreen?color=blue)
![Static Badge](https://img.shields.io/badge/platform-unix-brightgreen?color=blue)



## 🌟 Introduction


This is low resorse consuming smart TTS for Twitch Chat.

![DEMO:](https://github.com/timealtair/TwitchChatTTS/blob/main/demo.gif)

## 🗂️ Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## ✨ Features
1. Use 'TAB' button for smart commands autocomplete
2. Smart remove repeats from messages
3. At that moments supports console locales: 'en', 'ru'
4. Low resorse usage
5. Auto diagnastics before each run
6. Full cli control without gui needed

## 💻 Installation
Windows:
1. Clone or Download and unzip to empty directory
2. Run compile_win.cmd
3. Done!

Unix:
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/repository-name.git
2. Install requirements via python >= 3.10
   ```bash
   pip install -U -r requirements.txt
2. Compile to executable
   ```bash
   pyinstaller  --onefile --name twitch_chat_tts --icon=./source/twitch_chat_tts.ico ./source/main.py

## 💬 Usage:
1. Run TwitchChatTTS.exe or twitch_chat_tts
2. Select your locale
3. Folow instuction for first run config
4. Done!

