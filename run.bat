@echo off
REM This script opens the default browser with the server address and starts the server


REM Automatically opening the app in the default web browser
start http://127.0.0.1:8080

REM Run the application using Hypercorn
pipenv run hypercorn --bind=127.0.0.1:8080 app:app