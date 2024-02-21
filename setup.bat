@echo off
REM This script checks python 3 is installed and downloads, installs dependencies and sets up the database

REM Check for Python version 3.6 or newer
python --version 2>&1 | findstr /R "Python 3\.[6-9] Python 3\.[1-9][0-9]" > nul
if errorlevel 1 (
    echo Python 3.6 or newer is required.
    pause
    exit /b 1
)

REM Install requirements
pip install -r requirements.txt

REM Generate prisma executable 
prisma generate

REM Create db file and push schema to db
prisma db push

REM Notify use to use ./run.bat to run the web app in the future
msg * "Dependencies have been installed and the database has been setup. Please use ./run.sh to start the program" 
pause