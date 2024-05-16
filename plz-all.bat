@echo off

set DIR=%~dp0

cd /d %DIR%

python3 plex-localization-zh.py --all

pause
