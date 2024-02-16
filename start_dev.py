from app import app
import webbrowser


if __name__ == "__main__":
    webbrowser.open("http://localhost:5000/", new=2)
    app.run(debug=True, port=5000)
