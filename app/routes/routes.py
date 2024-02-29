from flask import render_template, request
from app import app
from prisma.models import Location


@app.route("/forest_green")
def tasks():
    return render_template("forestgreen.html")


@app.route("/documentation")
def documentation_page():
    return render_template("documentation.html")


@app.route("/")
def index():
    query = request.args.get("search")
    if query:
        locations = Location.prisma().find_many(where={"name": {"contains": query}})

    else:
        locations = Location.prisma().find_many()
    return render_template("index.html", locations=locations)


@app.route("/add_run")
def add_run():
    return render_template("add_run.html")


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
