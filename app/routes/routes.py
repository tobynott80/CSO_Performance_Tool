from flask import render_template
from app import app
from prisma.models import Location

@app.route('/forest_green')
def tasks():
    return render_template('forestgreen.html')

@app.route("/")
def index():
    locations = Location.prisma().find_many()
    return render_template("index.html", locations=locations)

@app.route("/add_run")
def add_run():
    return render_template("add_run.html")
