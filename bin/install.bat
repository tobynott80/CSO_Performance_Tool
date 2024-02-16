@echo off
REM This script checks python 3 is installed and downloads, installs dependencies and runs the server

REM Check for Python version 3.6 or newer
python --version 2>&1 | findstr /R "Python 3\.[6-9] Python 3\.[1-9][0-9]" > nul
if errorlevel 1 (
    echo Python 3.6 or newer is required.
    pause
    exit /b 1
)
REM Check if the repo has already been cloned
if exist arupwaterquality (
    echo arupwaterquality already exists.
    echo Please remove or rename the directory and run this script again.
    pause
    exit /b 1
)

REM Clone the repository
git clone https://git.cardiff.ac.uk/c2062405/arupwaterquality.git
cd arupwaterquality

REM Install requirements using pip
pip install -r requirements.txt

REM Automatically opening the app in the default web browser
start http://127.0.0.1:8080

REM Run the application using Waitress
python -m waitress --host=127.0.0.1 --port=8080 app:app


echo.
echo The project has been installed in %cd%
echo To start the app in the future, run the run.bat file.
pause