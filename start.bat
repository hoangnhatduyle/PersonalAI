@echo off
title Personal AI - Launcher

:: ── Configure your virtual environment path here ─────────
:: Leave blank to auto-detect (looks for venv, .venv, env in project root)
set VENV_PATH=

:: ─────────────────────────────────────────────────────────
set ROOT=%~dp0

:: Auto-detect venv if not set manually
if "%VENV_PATH%"=="" (
    if exist "%ROOT%venv\Scripts\activate.bat"  set VENV_PATH=%ROOT%venv
    if exist "%ROOT%.venv\Scripts\activate.bat" set VENV_PATH=%ROOT%.venv
    if exist "%ROOT%env\Scripts\activate.bat"   set VENV_PATH=%ROOT%env
)

if "%VENV_PATH%"=="" (
    echo [ERROR] No virtual environment found.
    echo Set VENV_PATH at the top of this script, e.g.:
    echo   set VENV_PATH=C:\Users\hoang\Envs\personal_ai
    pause
    exit /b 1
)

echo.
echo  Virtual env : %VENV_PATH%
echo  Backend     ^> http://localhost:7860
echo  Frontend    ^> http://localhost:3000
echo.

:: Start backend in its own window with venv activated
start "Personal AI - Backend" cmd /k "call "%VENV_PATH%\Scripts\activate.bat" && cd /d "%ROOT%" && python app.py"

timeout /t 2 /nobreak > nul

:: Start frontend in its own window
start "Personal AI - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo  Both services are starting in separate windows.
pause > nul
