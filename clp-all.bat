@echo off

set DIR=%~dp0

cd /d %DIR%

python3 chinese-localization-for-plex.py --all

pause
