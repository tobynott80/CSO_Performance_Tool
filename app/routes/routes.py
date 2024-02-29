from flask import render_template
from app import app
from prisma.models import Location

@app.route("/forest_green")
def tasks():
    return render_template("forestgreen.html")

@app.route("/")
def index():
    locations = Location.prisma().find_many()
    return render_template("index.html", locations=locations)

@app.route("/add_run")
def add_run():
    return render_template("add_run.html")

<<<<<<< app/routes/routes.py
@app.route("/docs")
def documentation_page():
    return render_template("/docs.html")

@app.route("/docs/getting_started")
def docs_one():
    return render_template("/docs/getting_started.html")

@app.route("/docs/test_1_dry_day")
def docs_two():
    return render_template("/docs/test_1_dry_day.html")

@app.route("/docs/test_2_rainfall_discharge")
def docs_three():
    return render_template("/docs/test_2_rainfall_discharge.html")

@app.route("/settings")
def setting_page():
    return render_template("settings.html")

@app.route("/location/<locid>")
def showRuns(locid):
    # Fetch the location, make sure correct then return the page
    return render_template("forestgreen.html")

@app.route("/location/<locid>/run/create")
def createRun(locid):
    # Fetch the location, make sure correct then return the create run page
    return render_template("runs/create.html")

