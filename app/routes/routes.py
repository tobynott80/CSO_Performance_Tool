from quart import render_template, request
from app import app
from app.helper.database import initDB
from math import ceil

db = None


@app.before_serving
async def initializeDB():
    global db
    db = await initDB()


@app.route("/forest_green")
async def tasks():
    return await render_template("forestgreen.html")


async def getPaginatedLocations(page, limit):
    skip = (page - 1) * limit  # Correctly calculate `skip` inside the function
    locations = await db.location.find_many(skip=skip, take=limit)  # Use `take` for consistency with Prisma's terminology
    return locations

async def getTotalLocations():
    total = await db.location.count()
    return total

@app.route("/")
async def index():
    query = request.args.get("search")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    if query:
        total = await db.location.count(where={"name": {"contains": query}})
        locations = await db.location.find_many(where={"name": {"contains": query}}, skip=(page - 1) * limit, take=limit)
    else:
        total = await getTotalLocations()
        locations = await getPaginatedLocations(page, limit)  # Correctly pass `page` and `limit`

    total_pages = ceil(total / limit)
    return await render_template("index.html", locations=locations, total_pages=total_pages, current_page=page, search=bool(query))



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
