# Arup Water Quality

## Automatic Install

Download and run the [installer batch script](https://git.cardiff.ac.uk/c2062405/arupwaterquality/uploads/707cb509ea2c8df99ef105898bf5c84c/install.bat) in the directory you wish to keep the program. (This might not work with certain antiviruses)

## Manual Install

1. Clone/Download this repo
2. Install requirements
   `pip install -r requirements.txt`
3. Run the following to start the server
   `waitress-serve.exe --host 127.0.0.1 app:app`
4. Navigate to `http://127.0.0.1:8080` in a browser
