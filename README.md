# Arup Water Quality

[![pipeline status](https://git.cardiff.ac.uk/c2062405/arupwaterquality/badges/main/pipeline.svg)](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/commits/main)
[![Latest Release](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/badges/release.svg)](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/releases)

This tool provides a front end to easily run and track GN066 tests. We are using a locally hosted [Quart](https://quart.palletsprojects.com/en) server and SQLite.

This tool currently only supports Windows 10/11.

## Install

### Prerequisites

Python >=3.11 must be installed on the system and [on the path](https://www.geeksforgeeks.org/how-to-add-python-to-windows-path/). If there are multiple python versions on your system, please setup the virtual environment manually with `pipenv install --python 3.11` before running `./setup.bat` in step 2 to ensure the correct version of python is used.

### Initial Installation

1. Clone/Download this repo
2. Install requirements by running the setup batch file
   `./setup.bat`
3. Run the following to start the server
   `./run.bat`
4. Navigate to `http://127.0.0.1:8080` in a browser

> Please note: There is a known issue with some networks where the Prisma binary certificate is invalidated - breaking the project setup. If you run into this problem, please run `$ENV:NODE_TLS_REJECT_UNAUTHORIZED=0` before `./setup.bat` in step 2.

### Running

Once the initial setup is complete, running `./run.bat` will start the application

## Alternative Dowloads

As the client does not have access to the Cardiff University GitLab service, we have a alternative host on [GitHub](https://github.com/tobynott80/ArupReleases/releases). Every commit on main branch is tagged, zipped and uploaded to the GitHub repo.

## Development Mode

Run `pipenv run py start_dev.py` to run the flask server in debug mode.

## Wiki

All onboarding information and notes are found on our [Notion Wiki](https://tobynott.notion.site/4fbea9d1184441e4a3ab7853ff5a9156?v=069d73cb3d3b4f3297784295dcee2f26).
