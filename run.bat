@echo off

REM Automatically opening the app in the default web browser
start http://127.0.0.1:8080

REM Run the application using Waitress
python -m waitress --host=127.0.0.1 --port=8080 app:app