from quart import Blueprint, render_template, request, redirect, session, url_for
from app.helper.database import initDB
from datetime import date
import asyncio
import time

import pandas as pd
from app.gn066_tests.csvHandler import csvReader, csvWriter
from app.gn066_tests import analysis
from app.gn066_tests import visualisation as vis
from app.gn066_tests.stats import timeStats, spillStats
from threading import Thread, enumerate

pd.options.mode.chained_assignment = None  # default='warn'

run_blueprint = Blueprint("run", __name__)

db = None
runs_tracker = {}


@run_blueprint.before_app_serving
async def initializeDB():
    global db
    db = await initDB()


@run_blueprint.route("/create/step1", methods=["POST"])
async def createRunStep1():
    # Use sessions to save step 1 data and then use it when submitting step 2 to create a run
    data = (await request.form).to_dict()
    if data is None:
        return redirect("/")
    if "loc" not in data:
        return redirect("/")
    else:
        session["loc"] = data.pop("loc")
    # If no run name given, set one with the ID from prisma? eg: Run 1
    session["run_name"] = data.pop("run_name", "New Run")
    session["run_desc"] = data.pop("run_desc", "N/A")
    session["run_date"] = data.pop("run_date", date.today())
    tests = []
    for test in data:
        if data[test] == "on":
            tests.append(test)
    session["tests"] = tests
    print(session)
    return redirect(url_for(f"createRun", locid=session["loc"], step=2))


@run_blueprint.route("/create/step2", methods=["POST"])
async def createRunStep2():
    global runs_tracker

    if "loc" not in session:
        # If no loc found, invalid since no session data
        return redirect("/")

    run = {
        "id": await getNextRunID(),
        "locationID": session["loc"],
        "name": session["run_name"],
        "description": session["run_desc"],
        "date": session["run_date"],
        "tests": session["tests"],
        "progress": {}
    }

    await db.runs.create(data={
        "id": run["id"],
        "date": run["date"],
        "locationID": run["locationID"],
        "name": run["name"],
        "description": run["description"],
    })

    # Delete session data since not needed in client side
    # session.pop("loc")
    # session.pop("run_name")
    # session.pop("run_desc")
    # session.pop("run_date")
    # session.pop("tests")

    files = await request.files
    print(files)

    runs_tracker[str(run["id"])] = run

    for test in run["tests"]:
        if test == "test-1" or test == "test-2":
            # Do checks to ensure the appropriate files are here
            if "rainfall-stats" not in files or "spill-stats" not in files:
                # TODO: Add a flash message to notify user of issue
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))
            test12thread = Thread(
                target=test1and2callback,
                args=(
                    files["rainfall-stats"],
                    (files["spill-stats"], "None", run["name"]),
                    [1, 2],
                    run
                ),
            )
            test12thread.start()
        if (test == "test-3"):
            # Do checks to ensure the appropriate files are here
            test3thread = Thread(
                target=test3callback,
                args=(
                    run
                ),
            )
            test3thread.start()

    return "helo", 200
    # return await render_template("runs/create_two.html")


@run_blueprint.route("/status", methods=["GET"])
async def checkStatus():
    global runs_tracker
    return runs_tracker


async def getNextRunID():
    result = await db.runs.find_first(order={"id": "desc"})
    nextID = 1
    if result:
        nextID = result.id + 1
    return nextID


def test1and2callback(rainfall_file, spills_baseline, tests, run):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # loop.run_until_complete(createTests1andor2(rainfall_file, spills_baseline, tests))
    loop.run_until_complete(createTests1andor2(
        rainfall_file, spills_baseline, tests, run))
    loop.close()
    return


def test3callback(run):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # loop.run_until_complete(createTests1andor2(rainfall_file, spills_baseline, tests))
    loop.run_until_complete(createTest3(run))
    loop.close()


async def createTests1andor2(rainfall_file, spills_baseline, tests, run):
    global runs_tracker
    starttime = time.perf_counter()
    heavy_rain = 4

    # Read CSV and Reformat
    df_rain_dtindex = csvReader.init(rainfall_file)
    runs_tracker[str(run["id"])]["progress"]["test-2"] = 20
    runs_tracker[str(run["id"])]["progress"]["test-1"] = 20

    csvReader.readCSV(df_rain_dtindex)
    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20

    df, spills_df = analysis.sewage_be_spillin(
        spills_baseline, df_rain_dtindex, heavy_rain
    )
    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20

    vis.timeline_visual(spills_baseline, df,
                        vis.timeline_start, vis.timeline_end)
    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20
    perc_data = timeStats.time_stats(df, spills_baseline)
    runs_tracker[str(run["id"])]["progress"]["test-1"] += 10
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 10
    all_spill_classification, spill_count_data = spillStats.spill_stats(
        spills_df, df, tests
    )
    runs_tracker[str(run["id"])]["progress"]["test-1"] += 10
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 10

    summary = pd.merge(perc_data, spill_count_data, on="Year")
    endtime = time.perf_counter()
    print("Elapsed Time: ", endtime - starttime)

    # csvWriter.writeCSV(df, summary, all_spill_classification)


async def createTest3(run):
    global runs_tracker

    runs_tracker[str(run["id"])]["progress"]["test-3"] = 100
    return
