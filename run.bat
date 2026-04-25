@echo off
chcp 65001 >nul
TITLE PHANTOM BOT
color 0B
"%~dp0venv\Scripts\python.exe" "%~dp0main.py"
pause
