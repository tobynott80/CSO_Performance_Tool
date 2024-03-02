from quart import render_template, request, redirect, session
from app import app
from app.helper.database import initDB

db = None


@app.before_serving
async def initializeDB():
    global db
    db = await initDB()


@app.route("/forest_green")
async def tasks():
    return await render_template("forestgreen.html")


@app.route("/")
async def index():
    query = request.args.get("search")
    if query:
        locations = await db.location.find_many(where={"name": {"contains": query}})
        return await render_template("index.html", locations=locations, search=True)

    else:
        locations = await db.location.find_many()
        return await render_template("index.html", locations=locations, search=False)


@app.route("/add_run")
async def add_run():
    return await render_template("add_run.html")


@app.route("/docs")
async def documentation_page():
    return await render_template("/docs.html")


@app.route("/docs/getting_started")
async def docs_one():
    return await render_template("/docs/getting_started.html")


@app.route("/docs/test_1_dry_day")
async def docs_two():
    return await render_template("/docs/test_1_dry_day.html")


@app.route("/docs/test_2_rainfall_discharge")
async def docs_three():
    return await render_template("/docs/test_2_rainfall_discharge.html")


@app.route("/settings")
async def setting_page():
    return await render_template("settings.html")


@app.route("/<locid>")
async def showRuns(locid):
    # Fetch the location, make sure correct then return the page
    return await render_template("forestgreen.html")


@app.get("/<locid>/create")
async def createRun(locid):
    # Redirect if no number
    if (not locid.isnumeric()):
        return redirect("/")

    loc = await db.location.find_first(
        where={'id': int(locid)}
    )
    if (loc == None):
        # Redirect if not a valid location ID
        return redirect("/")
    step = int(request.args.get('step')) if request.args.get('step') else 1

    if ('loc' in session):
        # Reset session when in starting step in new location
        if (session["loc"] != locid):
            session.pop("loc")
            session.pop("run_name")
            session.pop("run_desc")
            session.pop("run_date")
            session.pop("tests")
            step = 1
    elif 'loc' not in session:
        # Set step to 1 if no session data found 
        step = 1

    return await render_template(f"runs/{'create_one' if step == 1 else 'create_two'}.html", loc=loc, step=step, session=session)
