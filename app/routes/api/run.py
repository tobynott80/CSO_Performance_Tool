from quart import Blueprint, render_template, request, redirect, session, url_for
import asyncio
# from asyncio import create_task, all_tasks
from datetime import date

import pandas as pd
from app.gn066_tests.csvHandler import csvReader, csvWriter
from app.gn066_tests import analysis
from app.gn066_tests import visualisation as vis
from app.gn066_tests.stats import timeStats, spillStats
pd.options.mode.chained_assignment = None  # default='warn'

run_blueprint = Blueprint("run", __name__)


@run_blueprint.route("/create/step1", methods=["POST"])
async def createRunStep1():
    # Use sessions to save step 1 data and then use it when submitting step 2 to create a run
    data = (await request.form).to_dict()
    if (data is None):
        return redirect("/")
    if 'loc' not in data:
        return redirect("/")
    else:
        session["loc"] = data.pop("loc")
    # If no run name given, set one with the ID from prisma? eg: Run 1
    session["run_name"] = data.pop("run_name", "New Run")
    session["run_desc"] = data.pop("run_desc", "N/A")
    session["run_date"] = data.pop("run_date", date.today())
    tests = []
    for test in data:
        if (data[test] == "on"):
            tests.append(test)
    session["tests"] = tests
    print(session)
    return redirect(url_for(f"createRun", locid=session['loc'], step=2))


@run_blueprint.route("/create/step2", methods=["POST"])
async def createRunStep2():
    # from app import app
    if ('loc' not in session):
        # If no loc found, invalid since no session data
        return redirect("/")

    run = {"name": session["run_name"],
           "desc": session["run_desc"], "date": session["run_date"], "tests": session["tests"]}

    # Delete session data since not needed in client side
    # session.pop("loc")
    # session.pop("run_name")
    # session.pop("run_desc")
    # session.pop("run_date")
    # session.pop("tests")

    files = await request.files
    print(files)
    for test in run["tests"]:
        if (test == "test-1" or test == "test-2"):
            # Do checks to ensure the appropriate files are here
            if ("rainfall-stats" not in files or "spill-stats" not in files):
                # TODO: Add a flash message to notify user of issue
                return redirect(url_for(f"createRun", locid=session['loc'], step=2))

    if ('runs' not in session):
        # Initialize runs for tracking tasks
        session["runs"] = {}

    loop = asyncio.get_event_loop()
    loop.create_task(createTests1andor2(
        files["rainfall-stats"], (files["spill-stats"], "None", run["name"]), [1, 2]))

    # app.add_background_task(createTests1andor2, files["rainfall-stats"], (files["spill-stats"], "None", run["name"]), [1,2])
    # session["runs"][1]

    print(session["runs"])
    return "helo", 200
    # return await render_template("runs/create_two.html")


@run_blueprint.route("/status", methods=["GET"])
async def checkStatus():
    tasks = asyncio.all_tasks()
    for task in tasks:
        print(f'> {task.get_name()}, {task.get_coro()}')
    print(session["runs"])
    return "logged tasks"


async def createTests1andor2(rainfall_file, spills_baseline, tests):
    heavy_rain = 4

    # Read CSV and Reformat
    df_rain_dtindex = csvReader.init(rainfall_file)
    csvReader.readCSV(df_rain_dtindex)

    df, spills_df = analysis.sewage_be_spillin(
        spills_baseline, df_rain_dtindex, heavy_rain)
    vis.timeline_visual(spills_baseline, df,
                        vis.timeline_start, vis.timeline_end)

    perc_data = timeStats.time_stats(df, spills_baseline)

    all_spill_classification, spill_count_data = spillStats.spill_stats(
        spills_df, df, tests)

    summary = pd.merge(perc_data, spill_count_data, on='Year')

    csvWriter.writeCSV(df, summary, all_spill_classification)
