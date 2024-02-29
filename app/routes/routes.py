from flask import redirect, request, render_template
from app import app
from prisma.models import Location


@app.route('/forest_green')
def tasks():
    return render_template('forestgreen.html')


@app.route("/documentation")
def documentation_page():
    return render_template("documentation.html")


@app.route("/")
def index():
    locations = Location.prisma().find_many()
    return render_template("index.html", locations=locations)


@app.route("/<locid>")
def showRuns(locid):
    # Fetch the location, make sure correct then return the page
    return render_template("forestgreen.html")


@app.get("/<locid>/create")
def createRun(locid):
    if (not locid.isnumeric()):
        # Redirect if no number
        return redirect("/")
    loc = Location.prisma().find_first(
        where={'id': int(locid)}
    )
    if (loc == None):
        # Redirect if not a valid location ID
        return redirect("/")
    step = int(request.args.get('step')) if request.args.get('step') else 1
    return render_template(f"runs/{'create_one' if step == 1 else 'create_two'}.html", loc=loc, step=step)
