@echo off
REM This script checks that python =>3.11 is intalled, opens the default browser with the server address and starts the server

REM Check for Python version 3.11 or newer
python --version 2>&1 | findstr /R "Python 3\.(?:1[1-9]|[2-9]\d)" > nul
if errorlevel 1 (
    echo Python 3.11 or newer is required.
    echo Please download and install Python 3.11 or newer from https://www.python.org/downloads/ and set it as the default python version.
    pause
    exit /b 1
)

REM Automatically opening the app in the default web browser
start http://127.0.0.1:8080

REM Run the application using Hypercorn
pipenv run hypercorn --bind=127.0.0.1:8080 app:app