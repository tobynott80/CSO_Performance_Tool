@echo off
REM This script checks python =>3.11 is installed and downloads, installs dependencies and sets up the database

REM Check for Python version 3.11 or newer
python --version 2>&1 | findstr /R "Python 3\.[1-9][1-9]" > nul
if errorlevel 1 (
    echo Python 3.11 or newer is required.
    echo Please download and install Python 3.11 or newer from https://www.python.org/downloads/ and set it as the default python version.
    pause
    exit /b 1
)

REM Install python virtual environment
pip install --user pipenv

REM Install requirements from Pipfile
pipenv install

REM Generate prisma executable 
pipenv run prisma generate

REM Create db file and push schema to db
pipenv run prisma db push

REM Preload the database with tests
pipenv run py ./scripts/load-db.py

REM Notify use to use ./run.bat to run the web app in the future
msg * "Dependencies have been installed and the database has been setup. Please use ./run.bat to start the program" 
pause