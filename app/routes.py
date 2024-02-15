from flask import render_template
from app import app

@app.route('/forest_green')
def tasks():
    return render_template('forestgreen.html')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_run")
def add_run():
    return render_template("add_run.html")
