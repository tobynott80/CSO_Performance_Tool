from quart import (
    render_template,
    render_template_string,
    request,
    redirect,
    session,
    send_file,
    abort,
)
from app import app
from app.helper.database import initDB
from math import ceil
import os
import app.gn066_tests.config as config

db = None


@app.before_serving
async def initializeDB():
    """
    Initializes the database connection.

    This function is called before serving the application and initializes a global prisma variable to access the database.

    Returns:
        None
    """
    global db
    db = await initDB()


async def getPaginatedLocations(page, limit):
    """
    Retrieves a paginated list of locations from the database.

    Args:
        page (int): The page number to retrieve.
        limit (int): The maximum number of locations per page.

    Returns:
        list: A list of locations retrieved from the database.
    """
    skip = (page - 1) * limit
    locations = await db.location.find_many(skip=skip, take=limit)
    return locations


@app.route("/")
async def index():
    """
    Renders the index.html template with paginated locations with support for a search query.

    Args:
        None

    Returns:
        The rendered index.html template with the following variables:
        - locations: A list of locations based on the search query or all locations if no query is provided.
        - total_pages: The total number of pages based on the number of locations and the limit per page.
        - current_page: The current page number.
        - search: The search query.
    """
    query = request.args.get("search")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    if query:
        total = await db.location.count(where={"name": {"contains": query}})
        locations = await db.location.find_many(
            where={"name": {"contains": query}}, skip=(page - 1) * limit, take=limit
        )
    else:
        total = await db.location.count()
        locations = await getPaginatedLocations(page, limit)

    total_pages = ceil(total / limit)
    return await render_template(
        "index.html",
        locations=locations,
        total_pages=total_pages,
        current_page=page,
        search=query,
    )


@app.route("/docs")
async def documentation_page():
    """
    Renders the documentation page.

    Returns:
        The rendered documentation page as a response.
    """
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


@app.route("/<int:locid>")
async def showRuns(locid):
    """
    Display the details of a specific location and update the visited locations list.

    Parameters:
    locid (int): The ID of the location to display.

    Returns:
    Response: The rendered template of the specific location page.
    """
    # Fetch the location details from the database
    location = await db.location.find_unique(where={"id": locid})

    if not location:
        return redirect("/")

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
    """
    Handler function for the '/<locid>/create' route. Renders the first step of
    the create runs routine.

    Args:
        locid (str): The location ID.

    Returns:
        Response: The rendered template for creating a run.
    """
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
    """
    View the details of a specific run. Gathers the run details from the DB and
    renders the results summary.

    Args:
        location_id (str): The ID of the location.
        run_id (str): The ID of the run.

    Returns:
        A template with the details of the run, including the location, run, and runTest.

    Raises:
        None.
    """

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    runTest = await db.runtests.find_many(
        where={
            "runID": run_id,
        },
    )
    if not runTest or len(runTest) < 1:
        return redirect(f"/{location_id}")

    data = {}

    for rt in runTest:
        res = await db.runtests.find_first(
            where={"id": rt.id},
            include={"test": True, "summary": True, "testThree": True},
        )
        if rt.status == "COMPLETED":
            if len(res.summary) > 0:
                val = {}
                count = 0
                for x in res.summary:
                    if x.year == "Whole Time Series":
                        val = x
                    else:
                        count += 1
                # setattr(val, "yearsCount", count)
                res.summary = dict(val)
                res.summary["yearsCount"] = count
            data[res.test.name] = res
            if res.test.name == "Test 2" and "Test 1" in data:
                # Test 1 data is made so duplicate all data for it aswell
                res.summary = data["Test 1"].summary
        else:
            data[res.test.name] = res

    return await render_template(
        "runs/results/results_root.html",
        location=location,
        run=run,
        runTest=runTest,
        data=data,
    )


@app.get("/<int:location_id>/<int:run_id>/visualisation")
async def view_visualisation(location_id, run_id):
    """
    View the visualization for a specific location and run.

    Args:
        location_id (str): The ID of the location.
        run_id (str): The ID of the run.

    Returns:
        The rendered visualization template for the specified location and run.
        If the run is not found or in progress, an error message is displayed.
    """
    location = await db.location.find_first(where={"id": location_id})
    run = await db.runs.find_first(where={"id": run_id})

    runTest = await db.runtests.find_first(
        where={
            "runID": run_id,
        }
    )
    if not (runTest):
        return await render_template_string(
            "Run not found or in progess. Try again later"
        )
    elif runTest.status != "COMPLETED":
        return await render_template_string("Run in progress. Please try again later")
    return await render_template(
        "runs/results/visualisation.html",
        location=location,
        run=run,
        runTest=runTest,
    )


@app.get("/<int:location_id>/<int:run_id>/results_test3")
async def test3_results(location_id, run_id):
    """
    Retrieve and render Test 3 results for a specific location and run.

    Args:
        location_id (str): The ID of the location.
        run_id (str): The ID of the run.

    Returns:
        str: The rendered template with Test 3 results, or an error message if the run or results are not found.
    """
    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    tests = await db.tests.find_first(
        where={"name": "Test 3"},
        include={
            "runsTests": {"where": {"runID": run_id}, "include": {"testThree": True}},
        },
    )

    if not tests:
        return redirect(f"/{location_id}/{run_id}")

    if tests.runsTests[0].status != "COMPLETED":
        return redirect(f"/{location_id}/{run_id}")

    # Handling the case where there are no Test 3 results found for the run
    if not tests.runsTests[0].testThree:
        message = "No Test 3 results found for this run."
        return await render_template_string("Message: {{message}}", message=message)

    # If Test 3 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_test3.html",
        location=location,
        run=run,
        test3_results=tests.runsTests[0].testThree,
    )


@app.route("/download/test3/<filename>")
async def download_test3(filename):
    """
    Download test 3 results if available.

    Args:
        filename (str): The name of the test 3 file to be downloaded.

    Returns:
        Response: The file to be downloaded as a response object. If unavailable
        raises a 404 for not found.
    """
    file_directory = config.test_three_outputs

    if ".." in filename or "/" in filename or "\\" in filename:
        abort(404)

    file_path = os.path.join(file_directory, filename)

    if not os.path.exists(file_path):
        abort(404)

    return await send_file(file_path, attachment_filename=filename)


@app.get("/<int:location_id>/<int:run_id>/results_dry_day")
async def dry_day_results(location_id, run_id):
    
    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "runsTests": {"where": {"runID": run_id}, "include": {"summary": True}},
        },
    )

    if not tests:
        return redirect(f"/{location_id}/{run_id}")

    if tests.runsTests[0].status != "COMPLETED":
        return redirect(f"/{location_id}/{run_id}")

    # Handling the case where there are no Test 1 results found for the run
    if not tests.runsTests[0].summary:
        message = "No Test 1 results found for this run."
        return await render_template_string("Message: {{message}}", message=message)

    # If Test 1 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_dry_day.html",
        location=location,
        run=run,
        dry_day_results=tests.runsTests[0].summary,
    )

@app.get("/<int:location_id>/<int:run_id>/results_unsatisfactory_spills")
async def unsatisfactory_spills_results(location_id, run_id):
    
    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "runsTests": {"where": {"runID": run_id}, "include": {"summary": True}},
        },
    )

    if not tests:
        return redirect(f"/{location_id}/{run_id}")

    if tests.runsTests[0].status != "COMPLETED":
        return redirect(f"/{location_id}/{run_id}")

    # Handling the case where there are no Test 1 results found for the run
    if not tests.runsTests[0].summary:
        message = "No Test 1 results found for this run."
        return await render_template_string("Message: {{message}}", message=message)

    # If Test 1 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_unsatisfactory_spills.html",
        location=location,
        run=run,
        unsatisfactory_spills_results=tests.runsTests[0].summary,
    )

