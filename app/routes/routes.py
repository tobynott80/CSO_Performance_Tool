from quart import render_template, render_template_string, request, redirect, session, jsonify
from app import app
from app.helper.database import initDB
from math import ceil
import pandas as pd
from pathlib import Path

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


@app.after_serving
async def closeDB():
    """
    Closes the database connection.

    This function is called after serving the application and gracefully disconnects the prisma instance.

    Returns:
        None
    """
    global db
    db = await db.disconnect()


@app.before_request
def init_session():
    """
    Makes the session permanent.
    """
    session.permanent = True


async def getPaginatedLocations(page, limit, include_runs=False):
    """
    Retrieves a paginated list of locations from the database.

    Args:
        page (int): The page number to retrieve.
        limit (int): The maximum number of locations per page.
        include_runs (boolean): Include runs relationship data
    Returns:
        list: A list of locations retrieved from the database.
    """
    skip = (page - 1) * limit
    if include_runs:
        locations = await db.location.find_many(
            skip=skip, take=limit, include={"runs": True}
        )
    else:
        locations = await db.location.find_many(skip=skip, take=limit)
    return locations

@app.route("/autocomplete", methods=["GET"])
async def autocomplete():
    """
    Autocomplete the location search query.

    Args:
        None

    Returns:
        A list of locations based on the search query.
        A list of runs based on the search query.
    """
    # fetches a list of locations
    query = request.args.get("q")
    locations_list = await db.location.find_many(
        where={"name": {"contains": query}}, 
        take=10, 
    )
    # fetches a list of runs based on the search query
    runs = await db.runs.find_many(
        where={"name": {"contains": query}}, 
        take=10, 
    )
    
    # Console Tests
    # print("================================")
    # print("QUERY: ", query)
    # print("----------Locations-------------")
    # print(locations_list)
    # print("----------Runs-------------")
    # print(runs)
    
    return {"locations": [location.model_dump() for location in locations_list], "runs": [run.model_dump() for run in runs]}


@app.route("/")
async def index():
    """
    Renders the index.html template with paginated locations with support for a search query.

    Args:
        None

    Returns:
        The rendered index.html template with the following variables:
        - locations: A list of locations based on the search query or all locations if no query is provided.
        - runs: A list of runs based on the search query or all runs if no query is provided.
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
            where={"name": {"contains": query}},
            skip=(page - 1) * limit,
            take=limit,
            include={"runs": True},
        )

    else:
        total = await db.location.count()
        locations = await getPaginatedLocations(page, limit, include_runs=True)

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
    if "colorblind_mode" not in session:
        session["colorblind_mode"] = "normal"
    colorblind_mode = session["colorblind_mode"]
    return await render_template("settings.html", colorblind_mode=colorblind_mode)


@app.route("/settings/colorblind_mode", methods=["POST"])
async def set_colorblind_mode():
    """
    Sets the colorblind mode for the session.

    This function expects a JSON payload with a "mode" key indicating the desired colorblind mode.
    Valid colorblind modes are "normal", "protanopia", "deuteranopia", and "tritanopia".
    """
    data = await request.get_json()
    mode = data.get("mode")
    if mode not in ["normal", "protanopia", "deuteranopia", "tritanopia"]:
        return {"error": "Invalid colorblind mode"}, 400
    session["colorblind_mode"] = mode
    return {"success": True}


@app.delete("/api/location/<int:locid>")
async def delete_location(locid):
    try:
        # Delete the runs associated with the location
        await db.runs.delete_many(where={"locationID": locid})

        # Delete the location from the database
        await db.location.delete(where={"id": locid})

        if "visited_locations" in session:
            session["visited_locations"] = [
                location
                for location in session["visited_locations"]
                if location["id"] != locid
            ]

        if "recent_runs" in session:
            # Filter out runs associated with the deleted location
            session["recent_runs"] = [
                run for run in session["recent_runs"] if run["location"] != locid
            ]

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.delete("/api/run/<int:runid>")
async def delete_run(runid):
    try:
        # Delete the run from the database
        await db.runs.delete(where={"id": runid})

        if "recent_runs" in session:
            session["recent_runs"] = [
                run for run in session["recent_runs"] if run["id"] != runid
            ]

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/<int:locid>")
async def showRuns(locid):
    """
    Display the details of a specific location and update the visited locations list.

    Parameters:
    locid (int): The ID of the location to display.

    Returns:
    Response: The rendered template of the specific location page.
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    runs = await getPaginatedRuns(page, limit, locid)

    # Fetch the location details from the database ----------------------------
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

    total = await db.runs.count(where={"locationID": locid})
    total_pages = ceil(total / limit)
    # Render the specific location page
    return await render_template(
        "locations_page.html",
        location=location,
        runs=runs,
        total_pages=total_pages,
        current_page=page,
    )


async def getPaginatedRuns(page, limit, locid):
    """
    Retrieves a paginated list of locations from the database.

    Args:
        page (int): The page number to retrieve.
        limit (int): The maximum number of locations per page.
        include_runs (boolean): Include runs relationship data
    Returns:
        list: A list of locations retrieved from the database.
    """
    skip = (page - 1) * limit

    runs = await db.runs.find_many(
        where={"locationID": locid}, include={"Assets": True}, skip=skip, take=limit
    )
    return runs


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
            session.pop("doneValidation")  # used in move from step 2 validate
            session.pop("multiAsset")  # used in checking for multiple assets
            step = 1
    elif "loc" not in session:
        # Set step to 1 if no session data found
        step = 1

    if step == 3:
        if "doneValidation" not in session or session["doneValidation"] == False:
            step = 2
        elif "multiAsset" not in session or session["multiAsset"] == False:
            step = 2
        # Step 3 requires file validation precheck and multiple assets to be true
        else:
            print(session["spillStats"]["path"])
            # OSError: [Errno 22] Invalid argument
            spill_data = pd.read_excel(session["spillStats"]["path"])

            # Seperate the spill_Data excel file into individual assets based on the ID column
            assets = spill_data["ID"].unique()
            print(assets)

            return await render_template(
                "runs/create_three.html",
                loc=loc,
                step=step,
                session=session,
                assets=assets,
            )

    return await render_template(
        f"runs/{'create_one' if step == 1 else ('create_two' if step == 2 else 'create_three')}.html",
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
        A template with the details of the run, including the location, run, and assetTest.

    Raises:
        None.
    """

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    assets = await db.assets.find_many(
        where={
            "runID": run_id,
        },
        include={"assetTests": {"include": {"test": True, "testThree": True}}},
    )
    if not assets or len(assets) < 1:
        return redirect(f"/{location_id}")

    resp = {
        "status": run.status
    }

    for asset in assets:
        asset_name = asset.name
        asset = dict(asset)
        resp[asset_name] = {}
        for assetTest in asset["assetTests"]:
            resp[asset_name][assetTest.test.name] = {}
            resp[asset_name][assetTest.test.name]["summary"] = {
                "dryPerc": 0,
                "heavyPerc": 0,
                "spillPerc": 0,
                "unsatisfactorySpills": 0,
                "substandardSpills": 0,
                "satisfactorySpills": 0,
                "totalIntensity": 0,
            }
            resp[asset_name][assetTest.test.name]["assetTest"] = dict(assetTest)
            if assetTest.test.name != "Test 3":
                # resp[asset_name][assetTest.test.name]["summary"] = {}
                whole_time_series_summary = await db.summary.find_first(
                    where={"assetTestID": assetTest.id, "year": "Whole Time Series"}
                )
                print(whole_time_series_summary)
                if whole_time_series_summary is None:
                    if "Test 1" in resp[asset_name]:
                        # In Test 2
                        resp[asset_name][assetTest.test.name] = resp[asset_name][
                            "Test 1"
                        ]
                else:
                    summarycount = await db.summary.count(
                        where={"assetTestID": assetTest.id}
                    )
                    resp[asset_name][assetTest.test.name]["summary"] = dict(
                        whole_time_series_summary
                    )
                    resp[asset_name][assetTest.test.name]["summary"]["yearsCount"] = (
                        summarycount - 1
                    )
                    # resp[assetTest.test.name]["assetTest"] = dict(assetTest)
    print(resp)
    if not assets or len(assets) < 1:
        return redirect(f"/{location_id}")

    if "recent_runs" not in session:
        session["recent_runs"] = []

    existing_run = next(
        (item for item in session["recent_runs"] if item["id"] == run_id), None
    )

    if existing_run:
        session["recent_runs"] = [
            run for run in session["recent_runs"] if run["id"] != run_id
        ]

    session["recent_runs"].insert(
        0, {"id": run_id, "name": run.name, "location": location_id}
    )
    session["recent_runs"] = session["recent_runs"][:5]

    return await render_template(
        "runs/results/results_root.html",
        location=location,
        run=run,
        assets=assets,
        resp=resp,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/visualisation")
async def view_visualisation(location_id, run_id, asset_id):
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

    if "colorblind_mode" not in session:
        session["colorblind_mode"] = "normal"

    assetTest = await db.assettests.find_first(
        where={
            "assetID": asset_id,
        }
    )
    if not (assetTest):
        return await render_template_string(
            "Run not found or in progess. Try again later"
        )
    elif assetTest.status != "COMPLETED":
        # Add better page here.
        return await render_template_string("Run in progress. Please try again later")
    match session["colorblind_mode"]:
        case "normal":
            colors = {
                "red": "red",
                "green": "green",
                "orange": "orange",
                "blue": "blue",
                "purple": "purple",
            }
        case "protanopia":
            colors = {
                "red": "darkblue",
                "green": "teal",
                "orange": "gold",
                "blue": "blue",
                "purple": "violet",
            }
        case "deuteranopia":
            colors = {
                "red": "darkblue",
                "green": "teal",
                "orange": "gold",
                "blue": "blue",
                "purple": "violet",
            }
        case "tritanopia":
            colors = {
                "red": "#ff0000",
                "green": "#444444",
                "orange": "#ff0000",
                "blue": "violet",
                "purple": "orange",
            }
    return await render_template(
        "runs/results/visualisation.html",
        location=location,
        run=run,
        assetTest=assetTest,
        colors=colors,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_test3")
async def test3_results(location_id, run_id, asset_id):
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
            "assetTests": {
                "where": {"assetID": asset_id},
                "include": {"testThree": True},
            },
        },
    )

    if not tests:
        return redirect(f"/{location_id}/{run_id}")

    # Handling the case where there are no Test 3 results found for the run
    if not tests.assetTests[0].testThree:
        message = "No Test 3 results found for this run."
        return await render_template_string("Message: {{message}}", message=message)    
    
    # If Test 3 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_test3.html",
        location=location,
        run=run,
        test3_results=tests.assetTests[0].testThree,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_dry_day")
async def dry_day_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    assettests = await db.assettests.find_many(
        where={"assetID": asset_id},
        include={
            "summary": True,
        },
    )

    if not assettests:
        return redirect(f"/{location_id}/{run_id}")

    # Check if summary is available
    summary_use = None
    for test in assettests:
        if test.summary and (test.summary == 1 or test.summary):
            summary_use = test.summary
            break

    if not summary_use:
        return redirect(f"/{location_id}/{run_id}")

    # If Test 1 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_dry_day.html",
        location=location,
        run=run,
        dry_day_results=summary_use,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_unsatisfactory_spills")
async def unsatisfactory_spills_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    assettests = await db.assettests.find_many(
        where={"assetID": asset_id},
        include={
            "summary": True,
        },
    )

    if not assettests:
        return redirect(f"/{location_id}/{run_id}")

    # Check if summary is available
    summary_use = None
    for test in assettests:
        if test.summary and (test.summary == 1 or test.summary):
            summary_use = test.summary
            break

    if not summary_use:
        return redirect(f"/{location_id}/{run_id}")

    # If Test 1 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_unsatisfactory_spills.html",
        location=location,
        run=run,
        unsatisfactory_spills_results=summary_use,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_substandard_spills")
async def substandard_spills_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    assettests = await db.assettests.find_many(
        where={"assetID": asset_id},
        include={
            "summary": True,
        },
    )

    if not assettests:
        return redirect(f"/{location_id}/{run_id}")

    # Check if summary is available
    summary_use = None
    for test in assettests:
        if test.summary and (test.summary == 1 or test.summary):
            summary_use = test.summary
            break

    if not summary_use:
        return redirect(f"/{location_id}/{run_id}")

    # If Test 1 results are found, pass them to your template
    return await render_template(
        "/runs/results/results_substandard_spills.html",
        location=location,
        run=run,
        substandard_spills_results=summary_use,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_heavy_perc")
async def heavy_perc_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    test1 = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {
                "where": {"assetID": asset_id},
                "include": {"summary": True},
            },
        },
    )

    print(test1)
    if not test1.assetTests:

        test1 = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {
                    "where": {"assetID": run_id},
                    "include": {"summary": True},
                },
            },
        )

    return await render_template(
        "/runs/results/results_heavy_perc.html",
        location=location,
        run=run,
        heavy_perc_results=test1.assetTests[0].summary,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_spill_perc")
async def spill_perc_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    test1 = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {
                "where": {"assetID": asset_id},
                "include": {"summary": True},
            },
        },
    )

    print(test1)
    if not test1.assetTests:

        test1 = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {
                    "where": {"assetID": asset_id},
                    "include": {"summary": True},
                },
            },
        )

    return await render_template(
        "/runs/results/results_spill_perc.html",
        location=location,
        run=run,
        spill_perc_results=test1.assetTests[0].summary,
    )


@app.get("/<int:location_id>/<int:run_id>/<int:asset_id>/results_storm_overflow")
async def storm_overflow_results(location_id, run_id, asset_id):

    location = await db.location.find_first(where={"id": location_id})
    if not location:
        return redirect("/")

    run = await db.runs.find_first(where={"id": run_id})
    if not run:
        return redirect(f"/{location_id}")

    test1 = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {
                "where": {"assetID": asset_id},
                "include": {"summary": True},
            },
        },
    )

    print(test1)
    if not test1.assetTests:

        test1 = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {
                    "where": {"assetID": asset_id},
                    "include": {"summary": True},
                },
            },
        )

    return await render_template(
        "/runs/results/results_storm_overflow.html",
        location=location,
        run=run,
        storm_overflow_results=test1.assetTests[0].summary,
    )
