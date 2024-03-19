from quart import render_template, render_template_string, request, redirect, session
from pprint import pprint
from app import app
from app.helper.database import initDB
from math import ceil

db = None


@app.before_serving
async def initializeDB():
    global db
    db = await initDB()


async def getPaginatedLocations(page, limit, include_runs=False):
    skip = (page - 1) * limit  
    if include_runs:
        locations = await db.location.find_many(skip=skip, take=limit, include={"runs": True})
    else:
        locations = await db.location.find_many(skip=skip, take=limit)
    return locations


@app.route("/")
async def index():
    query = request.args.get("search")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    if query:
        total = await db.location.count(where={"name": {"contains": query}})
        locations = await db.location.find_many(
            where={"name": {"contains": query}}, 
            skip=(page - 1) * limit, 
            take=limit,
            include={"runs": True}
        )
    else:
        total = await db.location.count()
        locations = await getPaginatedLocations(page, limit, include_runs=True)


    for location in locations:
        print(f"Location: {location.name}")
        print("Runs:")
        pprint(location.runs)
        print("-" * 20)
        
    total_pages = ceil(total / limit)
    return await render_template(
        "index.html",
        locations=locations,
        total_pages=total_pages,
        current_page=page,
        search=query,
    )


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


@app.delete("/api/location/<int:locid>")
async def delete_location(locid):
    try:
        # Delete the runs associated with the location
        await db.runs.delete_many(where={"locationID": locid})

        # Delete the location from the database
        await db.location.delete(where={"id": locid})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/<int:locid>")
async def showRuns(locid):

    # Fetch the location details from the database
    location = await db.location.find_unique(where={"id": locid},include={"runs": {"include": {"runsTests": True}}})

    # Add location details to session
    if "visited_locations" not in session:
        session["visited_locations"] = []

    # Check if location is already in visited locations and if not add it to the list
    existing_location = next(
        (item for item in session["visited_locations"] if item["id"] == locid), None
    )
    if existing_location:
        session["visited_locations"] = [
            loc for loc in session["visited_locations"] if loc["id"] != locid
        ]
    session["visited_locations"].insert(0, {"id": locid, "name": location.name})
    session["visited_locations"] = session["visited_locations"][:5]

    # Render the specific location page
    return await render_template("locations_page.html", location=location)


@app.get("/<locid>/create")
async def createRun(locid):
    # Redirect if no number
    if not locid.isnumeric():
        return redirect("/")

    loc = await db.location.find_first(where={"id": int(locid)})
    if loc == None:
        # Redirect if not a valid location ID
        return redirect("/")
    step = int(request.args.get("step")) if request.args.get("step") else 1

    if "loc" in session:
        # Reset session when in starting step in new location
        if session["loc"] != locid:
            session.pop("loc")
            session.pop("run_name")
            session.pop("run_desc")
            session.pop("tests")
            step = 1
    elif "loc" not in session:
        # Set step to 1 if no session data found
        step = 1

    return await render_template(
        f"runs/{'create_one' if step == 1 else 'create_two'}.html",
        loc=loc,
        step=step,
        session=session,
    )


@app.get("/<int:location_id>/<int:run_id>")
async def view_run(location_id, run_id):
    location = await db.location.find_first(where={"id": location_id})
    run = await db.runs.find_first(where={"id": run_id})

    runTest = await db.runtests.find_first(
        where={
            "runID": run_id,
        },
        include={
            "test": True,
            "spillEvent": True,
            "summary": {"where": {"year": "Whole Time Series"}},
        },
    )
    if not (runTest):
        return await render_template_string(
            "Run not found or in progess. Try again later"
        )
    elif runTest.status != "COMPLETED":
        return await render_template_string("Run in progress. Please try again later")
    return await render_template(
        "runs/results/results_root.html", location=location, run=run, runTest=runTest
    )

@app.get("/<int:location_id>/<int:run_id>/results_test3")
async def test3_results(location_id, run_id):
    location = await db.location.find_first(where={"id": location_id})
    run = await db.runs.find_first(where={"id": run_id})
    tests = await db.tests.find_first(
        where={"name": "Test 3"},
        include={
            "runsTests": {"where": {"runID": run_id}, "include": {"testThree": True}},
        },
    )

    if not (tests):
        return await render_template_string(
            "Run not found or in progess. Try again later"
        )
    
    elif tests.runsTests[0].status != "COMPLETED":
        return await render_template_string("Run in progress. Please try again later")
    
    # Handling the case where there are no Test 3 results found for the run
    if not tests.runsTests[0].testThree:
        message = "No Test 3 results found for this run."
        return await render_template_string(
            "Message: {{message}}", message=message
        )

    # If Test 3 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_test3.html", location=location, run=run, test3_results=tests.runsTests[0].testThree 
    )
