@echo off
rem --- PHANTOM SETUP ---
chcp 65001 >nul
TITLE PHANTOM BOT - Setup
color 0B

cls
if exist "banner.txt" (
    type "banner.txt"
)
echo.
echo ============================================================
echo  Procurando Python 3.12...
echo ============================================================
echo.

set "PYTHON="
set "VENV_DIR=%~dp0venv"

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    echo [OK] Python encontrado: AppData
) else if exist "C:\Python312\python.exe" (
    set "PYTHON=C:\Python312\python.exe"
    echo [OK] Python encontrado: C:\Python312
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON=python"
        echo [OK] Python encontrado: PATH
    )
)

if not defined PYTHON (
    echo [ERRO] Python 3.12 nao encontrado. Instale em python.org
    pause
    exit /b 1
)

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo [OK] Ambiente virtual detectado.
    echo [..] Tentando limpar venv antigo...
    rmdir /s /q "%VENV_DIR%" >nul 2>&1
    if exist "%VENV_DIR%\Scripts\python.exe" (
        echo [OK] Venv em uso, pulando recriacao...
        goto :INSTALL
    )
)

echo [1/3] Criando ambiente virtual...
"%PYTHON%" -m venv "%VENV_DIR%"

:INSTALL
echo [2/3] Instalando bibliotecas (Fixing pkg_resources)...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip "setuptools==69.5.1" --quiet
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "requirements.txt"

echo [3/3] Instalando Chromium...
"%VENV_DIR%\Scripts\python.exe" -m playwright install chromium

echo.
echo ============================================================
echo  [PHANTOM] TUDO PRONTO! Pode rodar o run.bat agora.
echo ============================================================
pause
