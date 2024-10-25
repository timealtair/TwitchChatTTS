@echo off

:: Make temp dir

mkdir temp

:: Change working dir to temp

cd temp

:: Download Python embedded zip
curl -o "python-3.10.0-embed-amd64.zip" "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip"

:: Unzip Python embedded distribution
PowerShell -Command "Expand-Archive -Path 'python-3.10.0-embed-amd64.zip' -DestinationPath 'python-3.10.0-embed-amd64'"

:: Create the ._pth file
(
    echo python310.zip
    echo .
    echo import site
) > python-3.10.0-embed-amd64\python310._pth

:: Download get-pip.py to install pip
curl -o "python-3.10.0-embed-amd64\get-pip.py" "https://bootstrap.pypa.io/get-pip.py"

:: Install pip using the embedded Python
python-3.10.0-embed-amd64\python.exe python-3.10.0-embed-amd64\get-pip.py

:: Install PyInstaller using pip
python-3.10.0-embed-amd64\Scripts\pip.exe install -U -r ..\requirements.txt

:: Create an executable for main.py
python-3.10.0-embed-amd64\Scripts\PyInstaller.exe --onefile --name TwitchChatTTS.exe --icon=../source/twitch_chat_tts.ico ../source/main.py

:: Move TwitchChatTTS.exe to base directory

mv -f dist\TwitchChatTTS.exe ..\TwitchChatTTS.exe

:: Remove temp dir

rm -rf ./temp

:: Done

echo Done, file save as TwitchChatTTS.exe

pause