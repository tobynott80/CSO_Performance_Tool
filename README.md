# Arup Water Quality

[![pipeline status](https://git.cardiff.ac.uk/c2062405/arupwaterquality/badges/main/pipeline.svg)](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/commits/main)
[![Latest Release](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/badges/release.svg)](https://git.cardiff.ac.uk/c2062405/arupwaterquality/-/releases)

This tool provides a front end to easily run and track GN066 tests. We are using a locally hosted [Flask](https://flask.palletsprojects.com/en/3.0.x/) server.

## Automatic Install

Download and run the [installer batch script](https://git.cardiff.ac.uk/c2062405/arupwaterquality/uploads/707cb509ea2c8df99ef105898bf5c84c/install.bat) in the directory you wish to keep the program. (This might not work with certain antiviruses)

## Alternative Dowloads

As the client does not have access to the Cardiff University GitLab service, we have a alternative host on [GitHub](https://github.com/tobynott80/ArupReleases/releases). Every commit on main branch is tagged, zipped and uploaded to the GitHub repo.

## Manual Install

1. Clone/Download this repo
2. Install requirements
   `pip install -r requirements.txt`
3. Run the following to start the server
   `waitress-serve.exe --host 127.0.0.1 app:app`
4. Navigate to `http://127.0.0.1:8080` in a browser

## Development Mode

Run start_dev.py to run the flask server in debug mode.

## Wiki

All onboarding information and notes are found on our [Notion Wiki](https://tobynott.notion.site/4fbea9d1184441e4a3ab7853ff5a9156?v=069d73cb3d3b4f3297784295dcee2f26).
