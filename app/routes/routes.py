from quart import render_template, request
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


@app.route("/location/<locid>")
async def showRuns(locid):
    # Fetch the location, make sure correct then return the page
    return await render_template("forestgreen.html")


@app.route("/location/<locid>/run/create")
async def createRun(locid):
    # Fetch the location, make sure correct then return the create run page
    return await render_template("runs/create.html")
