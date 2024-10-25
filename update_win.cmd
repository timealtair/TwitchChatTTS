@echo off

:: Remove old temp dir if exists
if exist temp (
    rmdir /S /Q temp
)

:: Make new temp dir
mkdir temp

:: Change current dir to temp
cd temp

:: Get latest update

curl -o "TwitchChatTTS-main.zip" ""

set "repo_url=https://github.com/timealtair/TwitchChatTTS/archive/refs/heads/main.zip"
set "output_file=TwitchChatTTS-main.zip"

curl -L -o "%output_file%" "%repo_url%"

:: Unzip it

PowerShell -Command "Expand-Archive -Path 'TwitchChatTTS-main.zip' -DestinationPath '.'"

:: Replace all data with updated

xcopy "TwitchChatTTS-main\*" ".." /S /I /Y

:: Go to parent dir

cd ..

:: Start compile script

compile_win.cmd

pause