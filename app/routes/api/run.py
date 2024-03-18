from quart import Blueprint, render_template, request, redirect, session, url_for, flash
from app.helper.database import initDB
import asyncio

import pandas as pd
from app.gn066_tests.csvHandler import csvReader, csvWriter
from app.gn066_tests import analysis
from app.gn066_tests import visualisation as vis
from app.gn066_tests.stats import timeStats, spillStats
from threading import Thread

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
        "locationID": int(session["loc"]),
        "name": session["run_name"],
        "description": session["run_desc"],
        "tests": session["tests"],
        "progress": {},
        "runids": []
    }

    await db.runs.create(data={
        "id": run["id"],
        "locationID": run["locationID"],
        "name": run["name"],
        "description": run["description"],
    })



    files = await request.files
    print(files)

    runs_tracker[str(run["id"])] = run

    onlyOnce = False

    for test in run["tests"]:
        if test == "test-1" or test == "test-2":

            # Check if appropriate files are uploaded
            if "rainfall-stats" not in files or "spill-stats" not in files:
                await flash("Missing required files. Please upload both Rainfall Stats and Spill Stats.", "error")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))
            
            # Check correct format
            if not files["rainfall-stats"].filename.endswith(('.xlsx', '.csv')) or not files["spill-stats"].filename.endswith(('.xlsx', '.csv')):
                await flash('Invalid file format. Please upload files in .xlsx or .csv format.', 'error')
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))
            
             # Rainfall Data Validation
            try:
                rainfall_data = pd.read_csv(files["rainfall-stats"].stream, skiprows=13)
                if "P_DATETIME" not in rainfall_data.columns:
                    await flash("Invalid Rainfall Stats file: 'P_DATETIME' column missing.", "error")
                    return redirect(url_for(f"createRun", locid=session["loc"], step=2))
                # Convert P_DATETIME to datetime
                rainfall_data["P_DATETIME"] = pd.to_datetime(rainfall_data["P_DATETIME"], format="%d/%m/%Y %H:%M:%S")
                rainfall_data = rainfall_data.set_index("P_DATETIME", drop=False)
            except Exception as e:
                await flash(f"Error reading Rainfall Stats file: {e}", "error")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Spill Stats Data Validation
            try:
                spill_data = pd.read_excel(files["spill-stats"].stream)
                required_columns = ["Start of Spill (absolute)", "End of Spill (absolute)"]
                missing_columns = [column for column in required_columns if column not in spill_data.columns]
                if missing_columns:
                    await flash("Missing required columns in Spill Stats file: " + ", ".join(missing_columns), "error")
                    return redirect(url_for(f"createRun", locid=session["loc"], step=2))
            except Exception as e:
                await flash(f"Error reading Spill Stats file: {e}", "error")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))


            # Connect Tests in DB to frontend tests
            testid = await db.tests.find_first(where={
                "name": "Test 1" if test == "test-1" else "Test 2"
            })

            runtest = await db.runtests.create(data={
                "runID": run["id"],
                "testID": testid.id,
                "status": "PROGRESS"
            })

            # Store RunTest ID for when running thread
            run["runids"].append(runtest.id)

            # If both Test 1 & 2 selected, ensure thread is only ran once
            if (onlyOnce == True):
                continue

            onlyOnce = True

            try:
                test12thread = Thread(
                    target=test1and2callback,
                    args=(
                        rainfall_data,
                        (files["spill-stats"], "None", run["name"]),
                        run
                    ),
                )
                test12thread.start()
                flash("Test 1 and 2 started successfully.", "success")
            except Exception as e:
                print("Error starting Test 1 and 2:", e)  # Log the error
                flash(f"Error starting Test 1 and 2: {e}", "error")

        if (test == "test-3"):
            # Do checks to ensure the appropriate files are here
            test3thread = Thread(
                target=test3callback,
                args=(
                    run
                ),
            )
            test3thread.start()


    # Delete session data since not needed in client side
    session.pop("loc")
    session.pop("run_name")
    session.pop("run_desc")
    session.pop("tests")

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


def test1and2callback(rainfall_data, spills_baseline, run):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(createTests1andor2(
        rainfall_data, spills_baseline, run))
    loop.close()
    return


def test3callback(run):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # loop.run_until_complete(createTests1andor2(rainfall_file, spills_baseline, tests))
    loop.run_until_complete(createTest3(run))
    loop.close()


async def createTests1andor2(rainfall_data, spills_baseline, run):
    from prisma import Prisma

    global runs_tracker
    db = Prisma()
    await db.connect()
    heavy_rain = 4

    # Read CSV and Reformat
    df_rain_dtindex = rainfall_data
    # df_rain_dtindex = csvReader.init(rainfall_file)

    runs_tracker[str(run["id"])]["progress"]["test-1"] = 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] = 20

    csvReader.readCSV(df_rain_dtindex)

    df, spills_df = analysis.sewage_be_spillin(
        spills_baseline, df_rain_dtindex, heavy_rain
    )

    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20

    vis.timeline_visual(spills_baseline, df,
                        vis.timeline_start, vis.timeline_end)
    perc_data = timeStats.time_stats(df, spills_baseline)

    runs_tracker[str(run["id"])]["progress"]["test-1"] += 10
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 10

    all_spill_classification, spill_count_data = spillStats.spill_stats(
        spills_df, df, [1, 2]
    )

    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20

    summary = pd.merge(perc_data, spill_count_data, on="Year")

    runs_tracker[str(run["id"])]["progress"]["test-1"] += 10
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 10

    # Save all results to SQLite database
    await saveSummaryToDB(db, run, summary)
    await saveSpillToDB(db, run, all_spill_classification)

    runs_tracker[str(run["id"])]["progress"]["test-1"] += 20
    runs_tracker[str(run["id"])]["progress"]["test-2"] += 20

    for test in run["runids"]:
        await db.runtests.update(
            where={
                'id': test
            },
            data={
                "status": "COMPLETED"
            })

    # Saves 300k worth of rows - can be done in background?
    await saveTimeSeriesToDB(db, run, df)

    # csvWriter.writeCSV(df, summary, all_spill_classification)


async def createTest3(run):
    global runs_tracker

    runs_tracker[str(run["id"])]["progress"]["test-3"] = 100
    return


async def saveSummaryToDB(db, run, summary):
    for index, row in summary.iterrows():
        await db.summary.create(data={
            "year": str(row['Year']),
            "dryPerc": row["Percentage of dry days (%)"],
            "heavyPerc": row["Percentage of year spills are allowed to start (%)"],
            "spillPerc": row[f"{run['name']} - Percentage of year spilling (%)"],
            "unsatisfactorySpills": row[f"{run['name']} - Unsatisfactory Spills"],
            "substandardSpills": row[f"{run['name']} - Substandard Spills"],
            "satisfactorySpills": row[f"{run['name']} - Satisfactory Spills"],
            "runTestID": run["runids"][0]
        })


async def saveTimeSeriesToDB(db, run, df):
    for index, row in df.iterrows():
        await db.timeseries.create(data={
            "dateTime": index,
            "intensity": row["Intensity"],
            "depth": row["Depth_x"],
            "rollingDepth": row["Rolling 1hr depth"],
            "classification": row["Classification"],
            "spillAllowed": row["Spill_allowed?"],
            "dayType": row["Day Type"],
            "result": row[run["name"]],
            "runTestID": run["runids"][0]
        })


async def saveSpillToDB(db, run, all_spill_classification):
    print(all_spill_classification)
    for index, row in all_spill_classification.iterrows():
        await db.spillevent.create(data={
            "start": row["Start of Spill (absolute)"],
            "end": row["End of Spill (absolute)"],
            "volume": row["Spill Volume (m3)"],
            "runName": run["name"],
            "maxIntensity": row["Max intensity in 24hrs preceding spill start (mm/hr)"],
            "maxDepthInHour": row["Max depth in an hour in 24hrs preceding spill start (mm/hr)"],
            "totalDepth": row["Total depth in 24hrs preceding spill start (mm)"],
            "test1": row["Test 1 Status"],
            "test2": row["Test 2 Status"],
            "classification": row["Classification"],
            "runTestID": run["runids"][0]
        })
