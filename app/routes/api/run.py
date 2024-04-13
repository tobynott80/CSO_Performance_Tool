from dataclasses import dataclass
import json
from quart import (
    Blueprint,
    make_response,
    request,
    redirect,
    session,
    url_for,
    flash,
)
from app.helper.database import initDB
import asyncio
import math
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
from app.gn066_tests.csvHandler import csvReader, csvWriter
from app.gn066_tests import analysis
from app.gn066_tests import visualisation as vis
from app.gn066_tests.stats import timeStats, spillStats
from threading import Thread
from app.gn066_tests.tests import test3
from app.gn066_tests import config

pd.options.mode.chained_assignment = None  # default='warn'
TMP_FOLDER = "tmp"

run_blueprint = Blueprint("run", __name__)


db = None
runs_tracker = {}


def safe_float_conversion(value, default=None):
    """Attempt to convert a value to float. Return default if conversion fails or value is not provided."""
    try:
        if value in (None, "", "None"):  # Checks if the input value is empty or None
            return default
        return float(value)
    except ValueError:
        return default


@run_blueprint.before_app_serving
async def initializeDB():
    """
    Initializes the database connection.

    This function is called before serving the application and initializes a global prisma variable to access the database.
    """
    global db
    db = await initDB()


@run_blueprint.after_app_serving
async def closeDB():
    """
    Closes the database connection.

    This function is called after serving the application and gracefully disconnects the prisma instance.

    Returns:
        None
    """
    global db
    db = await db.disconnect()


@run_blueprint.route("/create/step1", methods=["POST"])
async def createRunStep1():
    """
    API route for step 1 of run creation. Saves the given run name, description
    and tests picked to the session and redirects to step 2.

    Returns:
        A redirect response to step 2.
    """
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
    session["doneValidation"] = False
    tests = []
    for test in data:
        if data[test] == "on":
            tests.append(test)
    session["tests"] = tests
    print(session)
    return redirect(url_for(f"createRun", locid=session["loc"], step=2))


@run_blueprint.route("/create/step2/validate", methods=["POST"])
async def createRunStep2Validation():

    if "loc" not in session:
        # If no loc found, invalid since no session data
        return redirect("/")

    tests = session["tests"]

    files = await request.files

    resp = await checkTestValidation(tests, files)
    # resp = {success: true, message: "If Error", hasMultiAsset: false}
    if not resp:
        await flash("Something went wrong with validation", "error")
        return redirect(url_for(f"createRun", locid=session["loc"], step=1))

    if not resp["success"] or resp["success"] == False:
        await flash(resp["message"], "error")
        return redirect(url_for(f"createRun", locid=session["loc"], step=2))

    if "Baseline Stats Report" in files:
        path = await saveTempFile(files["Baseline Stats Report"])
        session["baselineStats"] = {
            "filename": files["Baseline Stats Report"].filename,
            "path": path,
        }

    if "rainfall-stats" in files:
        path = await saveTempFile(files["rainfall-stats"])
        session["rainfallStats"] = {
            "filename": files["rainfall-stats"].filename,
            "path": path,
        }

    if "spill-stats" in files:
        path = await saveTempFile(files["spill-stats"])
        session["spillStats"] = {
            "filename": files["spill-stats"].filename,
            "path": path,
        }

    session["doneValidation"] = True
    if resp["hasMultiAsset"]:
        session["multiAsset"] = True
        # Add session value for multi asset
    else:
        session["multiAsset"] = False
    return redirect(url_for(f"createRun", locid=session["loc"], step=2))


@run_blueprint.route("/create/step2", methods=["POST"])
async def createRunStep2():
    """
    API route for step 2, dispatches the job to the thread handler if no step 3 required.

    Returns:
        A redirect response to the created run page.

    """

    if "loc" not in session:
        # If no loc found, invalid since no session data
        return redirect("/")

    if "doneValidation" not in session or session["doneValidation"] == False:
        # If not completed validation precheck, redirect back
        return redirect(url_for(f"createRun", locid=session["loc"], step=2))

    form_data = await request.form
    formula_a_value = safe_float_conversion(form_data.get("formula-a"), default=None)
    consent_flow_value = safe_float_conversion(
        form_data.get("consent-flow"), default=None
    )

    if "multiAsset" in session and session["multiAsset"] == True:
        # Redirect to step 3 where they will select assets
        session["formulaA-val"] = formula_a_value
        session["consent-val"] = consent_flow_value
        return redirect(url_for(f"createRun", locid=session["loc"], step=3))



    # Create run since no multi assets
    run = await createRuns(session, formula_a_value, consent_flow_value)

    # Delete session data since not needed in client side
    session.pop("loc")
    session.pop("run_name")
    session.pop("run_desc")
    session.pop("tests")

    return redirect(f"/{run['locationID']}/{run['id']}")


async def saveTempFile(file):
    Path(TMP_FOLDER).mkdir(exist_ok=True)
    extension = file.filename.split(".")[-1]
    path = os.path.join(
        TMP_FOLDER, datetime.today().strftime("%d-%m-%Y_%H-%M-%S") + "." + extension
    )
    if extension == "xlsx":
        # NOT PERFORMANT, IF CAN DO BETTER PLS DO
        df = pd.read_excel(file)
        writer = pd.ExcelWriter(path, engine="xlsxwriter")
        df.to_excel(writer)
        writer.close()
    else:
        await file.save(path)
    return path
    # Delete tmp folder on every app run? ensure no stale files


@run_blueprint.route("/create/step3", methods=["POST"])
async def createRunStep3():
    """
    API route for step 3, the final step of the runs creation routine.
    Dispatches the job to the thread handler.

    Returns:
        A redirect response to the created run page.

    """
    # In step 2, based on multiAsset cookie it will either
    # redirect to step 3 or start run process and redirect to results page

    if "loc" not in session:
        # If no loc found, invalid since no session data
        return redirect("/")

    # Fetch the selected assets and fit them into the createRuns() common function (somehow)
    form_data = await request.form
    selectedAssets = list(form_data.keys())
    run = await createRuns(session, session["formulaA-val"], session["consent-val"], selectedAssets)

    # Delete session data since not needed in client side
    session.pop("loc")
    session.pop("run_name")
    session.pop("run_desc")
    session.pop("tests")    

    return redirect(f"/{run['locationID']}/{run['id']}")




# Only checks files validation
async def checkTestValidation(tests, files):

    resp = {"success": False, "message": "", "hasMultiAsset": False}

    onlyOnce = False
    for test in tests:
        if test == "test-1" or test == "test-2":

            # Check if appropriate files are uploaded
            if "rainfall-stats" not in files or "spill-stats" not in files:
                resp["message"] = (
                    "Missing required files. Please upload both Rainfall Stats and Spill Stats."
                )
                break

            # Check correct format
            if not files["rainfall-stats"].filename.endswith((".csv")) or not files[
                "spill-stats"
            ].filename.endswith((".xlsx")):
                resp["message"] = (
                    "Invalid file format. Please upload files the rainfall-stats as a .csv and spill-stats as a .xlsx."
                )
                break

            # Rainfall Stats Data Validation
            try:
                # Read the necessary rows for validation
                df_temp = pd.read_csv(
                    files["rainfall-stats"].stream,
                    skiprows=13,
                    nrows=10,
                    encoding="utf-8-sig",
                )

                # Check for the 'P_DATETIME' column
                if "P_DATETIME" not in df_temp.columns:
                    resp["message"] = (
                        "Invalid Rainfall Stats file: 'P_DATETIME' column missing."
                    )
                    break

            except Exception as e:
                resp["message"] = f"Error reading Rainfall Stats file: {e}"
                break

            # Reset file pointer to the beginning of the file
            files["rainfall-stats"].seek(0)

            # Spill Stats Data Validation
            try:
                spill_data = pd.read_excel(files["spill-stats"].stream)
                required_columns = [
                    "Start of Spill (absolute)",
                    "End of Spill (absolute)",
                    "Sim",
                    "ID",
                    "Spill Volume (m3)",
                ]
                missing_columns = [
                    column
                    for column in required_columns
                    if column not in spill_data.columns
                ]
                if missing_columns:
                    resp["message"] = (
                        "Please move Excel sheet to first place in sheet list."
                        + " Missing required columns in Spill Stats file: "
                        + ", ".join(missing_columns)
                    )
                    break

                # Check if there are multiple ID's in the Excel file

                if len(spill_data["ID"].unique()) > 1:
                    resp["hasMultiAsset"] = True

            except Exception as e:
                resp["message"] = "Error reading Spill Stats file: " + str(e)
                break

            resp["success"] = True

            # If both Test 1 & 2 selected, ensure thread is only ran once
            if onlyOnce == True:
                continue

            onlyOnce = True

        if test == "test-3":

            # Check if Baseline Stats Report is present
            if "Baseline Stats Report" not in files:
                resp["message"] = "Baseline Stats Report is required for Test 3"
                break

            # Correct format check
            if not files["Baseline Stats Report"].filename.endswith(
                (".xlsx", ".csv", ".xls")
            ):
                resp["message"] = (
                    "Invalid file format. Only '.xlsx', '.csv', and '.xls' files are supported."
                )
                break

            # Load the Excel file and checks whether sheet "Summary" exists
            try:
                df_pff = pd.read_excel(
                    files["Baseline Stats Report"].stream,
                    sheet_name="Summary",
                    header=1,
                    nrows=2,
                )
            except Exception as e:
                resp["message"] = (
                    "Error reading file, Please Input a valid Excel file. Error: "
                    + str(e)
                )
                break

            # Check if required columns are present
            required_columns = ["Peak PFF (l/s)", "Avg Initial PFF (l/s)", "Year"]
            missing_columns = [
                column for column in required_columns if column not in df_pff.columns
            ]
            if missing_columns:
                resp["message"] = "Missing required columns: " + ", ".join(
                    missing_columns
                )
                break
            resp["success"] = True
    return resp


async def createRuns(session, formula_a_value, consent_flow_value, selectedAssets=None):
    global runs_tracker

    run = {
        "id": await getNextRunID(),
        "locationID": int(session["loc"]),
        "name": session["run_name"],
        "description": session["run_desc"],
        "tests": session["tests"],
        "progress": {},
        "assets": {},
    }

    run["baselineStatsFile"] = (
        session["baselineStats"]["filename"] if "baselineStats" in session else None
    )
    run["rainfallStatsFile"] = (
        session["rainfallStats"]["filename"] if "rainfallStats" in session else None
    )
    run["spillStatsFile"] = (
        session["spillStats"]["filename"] if "spillStats" in session else None
    )

    await db.runs.create(
        data={
            "id": run["id"],
            "locationID": run["locationID"],
            "name": run["name"],
            "description": run["description"],
            "baselineStatsFile": run["baselineStatsFile"],
            "rainfallStatsFile": run["rainfallStatsFile"],
            "spillStatsFile": run["spillStatsFile"],
        }
    )

    runs_tracker[str(run["id"])] = run

    onlyOnce = False

    df = pd.read_excel(session["spillStats"]["path"])

    for assetName, assetData in df.groupby(pd.Grouper(key="ID")):
        # Loops over every asset

        # Ignore unselected assets (as they do not want it)
        if selectedAssets is not None:
            if assetName not in selectedAssets:
                continue

        asset = await db.assets.create(data={"name": assetName, "runID": run["id"]})
        run["assets"][asset.id] = {"name": assetName, "assettests": {}}

        for test in run["tests"]:
            if test == "test-1" or test == "test-2":
                # Connect Tests in DB to frontend tests
                testid = await db.tests.find_first(
                    where={"name": "Test 1" if test == "test-1" else "Test 2"}
                )
                if not testid:
                    # No tests in db, run setup script again
                    await flash(
                        "Server not setup properly, please run setup script again.",
                        "error",
                    )
                    return redirect(url_for(f"createRun", locid=session["loc"], step=1))

                assettest = await db.assettests.create(
                    data={
                        "assetID": asset.id,
                        "testID": testid.id,
                        "status": "PROGRESS",
                    }
                )

                run["assets"][asset.id]["assettests"][testid.name] = assettest.id

                # If both Test 1 & 2 selected, ensure thread is only ran once
                if onlyOnce == True:
                    continue

                onlyOnce = True
                test12thread = Thread(
                    target=test1and2callback,
                    args=(
                        session["rainfallStats"]["path"],
                        (assetData, "None", run["name"]),
                        run,
                        asset.id,
                    ),
                )
                test12thread.start()
            if test == "test-3":

                # Connect Tests in DB to frontend tests
                testid = await db.tests.find_first(where={"name": "Test 3"})
                if not testid:
                    # No tests in db, run setup script again
                    await flash(
                        "Server not setup properly, please run setup script again.",
                        "error",
                    )
                    return redirect(url_for(f"createRun", locid=session["loc"], step=1))

                assettest = await db.assettests.create(
                    data={
                        "assetID": asset.id,
                        "testID": testid.id,
                        "status": "PROGRESS",
                    }
                )

                # Store RunTest ID for when running thread
                run["assets"][asset.id]["assettests"][testid.name] = assettest.id

                test3thread = Thread(
                    target=test3callback,
                    args=(
                        formula_a_value,
                        consent_flow_value,
                        session["baselineStats"]["path"],
                        run,
                        asset.id,
                    ),
                )
                test3thread.start()

    return run


@dataclass
class ServerSentEvent:
    """
    Helper class to represent a server sent event.
    Adapted from: https://quart.palletsprojects.com/en/latest/how_to_guides/server_sent_events.html

    Attributes:
        data (str): The data to be sent in the event.
        event (str | None): The event name .
        id (int | None): The event ID.
        retry (int | None): The retry time in milliseconds.
    """

    data: str
    retry: int | None = 100
    event: str | None = None
    id: int | None = None

    def encode(self) -> bytes:
        """
        Encodes the SSE into bytestream.

        Returns:
            The encoded sse
        """
        message = f"data: {self.data}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.id is not None:
            message = f"{message}\nid: {self.id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        message = f"{message}\n\n"
        return message.encode("utf-8")


@run_blueprint.route("/status", methods=["GET"])
async def checkStatus():
    """
    Check the status of the runs tracker and send updates using server sent events.

    Adapted from: https://quart.palletsprojects.com/en/latest/how_to_guides/server_sent_events.html
    Returns:
        A response object for server sent events.
    """
    global runs_tracker
    if "text/event-stream" not in request.accept_mimetypes:
        return "Invalid request", 400

    async def send_events():
        while True:
            data = runs_tracker
            event = ServerSentEvent(json.dumps(data))
            yield event.encode()
            await asyncio.sleep(0.1)

    response = await make_response(
        send_events(),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response


async def getNextRunID():
    """
    Helper function to retrieve the next available run ID.

    Returns:
        int: The next available run ID.
    """
    result = await db.runs.find_first(order={"id": "desc"})
    nextID = 1
    if result:
        nextID = result.id + 1
    return nextID


def test1and2callback(rainfall_file, spills_baseline, run, assetid):
    """
    Callback function to execute tests 1 and 2.

    Args:
        rainfall_file (str): The path to the rainfall file.
        spills_baseline (str): The path to the spills baseline file.
        run (str): The run database information.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(createTests1andor2(rainfall_file, spills_baseline, run, assetid))
    loop.close()
    return


def test3callback(formula_a_value, consent_flow_value, baseline_stats_file, run, assetid):
    """
    Callback function to execute test 3.

    Args:
        formula_a_value (float): The value of formula A.
        consent_flow_value (float): The value of consent flow.
        baseline_stats_file (str): The file path of the baseline statistics file.
        run (str): The run database information.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        createTest3(formula_a_value, consent_flow_value, baseline_stats_file, run, assetid)
    )
    loop.close()


async def createTests1andor2(rainfall_file, spills_baseline, run, assetID):
    """
    Perform tests 1 and/or 2 on the given rainfall data and spills baseline.

    Args:
        rainfall_file (str): The path to the rainfall data file.
        spills_baseline (str): The path to the spills baseline data file.
        run (dict): The run database information.
    """
    from prisma import Prisma

    global runs_tracker
    db = Prisma()
    await db.connect()
    heavy_rain = 4

    runs_tracker[str(run["id"])]["progress"][
        "test-1&2"
    ] = "Importing files and reading data"

    # Read CSV and Reformat
    df_rain_dtindex = csvReader.init(rainfall_file)
    csvReader.readCSV(df_rain_dtindex)

    runs_tracker[str(run["id"])]["progress"][
        "test-1&2"
    ] = "Running Sewage Be Spilling Analysis"

    df, spills_df = analysis.sewage_be_spillin(
        spills_baseline, df_rain_dtindex, heavy_rain
    )
    # runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Visualising Data"
    # Does this need to be run?
    vis.timeline_visual(spills_baseline, df, vis.timeline_start, vis.timeline_end)

    rainfall_summary = csvReader.aggregate_rainfall_directly(df_rain_dtindex)

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Calculating Summary Stats"

    perc_data = timeStats.time_stats(df, spills_baseline)

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Calculating Spill Stats"

    all_spill_classification, spill_count_data = spillStats.spill_stats(
        spills_df, df, [1, 2]
    )
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Merging Dataframes"

    summary = pd.merge(perc_data, spill_count_data, on="Year")
    summary = pd.merge(summary, rainfall_summary, on="Year", how="left")

    # Save all results to SQLite database
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Saving summary to DB"
    await saveSummaryToDB(db, run, assetID, summary)
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Saving spills to DB"
    await saveSpillToDB(db, run, assetID, all_spill_classification)

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Saving timeseries to DB..."

    # Saves 300k worth of rows
    await saveTimeSeriesToDB(db, run, assetID, df)

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Completed"
    
    for test in run["assets"][assetID]["assettests"]:
        if test == "Test 1" or test == "Test 2":
            await db.assettests.update(
                where={"id": run["assets"][assetID]["assettests"][test]}, data={"status": "COMPLETED"}
            )
    # csvWriter.writeCSV(df, summary, all_spill_classification)


async def createTest3(formula_a_value, consent_flow_value, baseline_stats_file, run, assetID):
    """
    Perform Test 3 analysis and save the results to the database and an Excel file.

    Args:
        formula_a_value (float): The value of Formula A.
        consent_flow_value (float): The value of Consent FPF.
        baseline_stats_file (FileStorage): The baseline statistics file.
        run (dict): The run database information.
    """
    global runs_tracker

    runs_tracker[str(run["id"])]["progress"]["test-3"] = "Running FPF Calculations"

    df_pff = pd.read_excel(baseline_stats_file.stream, sheet_name="Summary", header=1)

    df_pff["Compliance Status"] = df_pff.apply(
        lambda row: test3.check_compliance(row, formula_a_value, consent_flow_value),
        axis=1,
    )
    df_pff["Just Formula A"] = df_pff.apply(
        lambda row: test3.check_formula_a(row, formula_a_value), axis=1
    )
    df_pff["Just Consent FPF"] = df_pff.apply(
        lambda row: test3.check_consent_fpf(row, consent_flow_value), axis=1
    )

    print(df_pff[["Year", "Compliance Status"]])
    print(df_pff[["Year", "Just Formula A"]])
    print(df_pff[["Year", "Just Consent FPF"]])

    from prisma import Prisma

    db = Prisma()
    await db.connect()
    await saveTest3ToDB(db, run, assetID, df_pff, formula_a_value, consent_flow_value)

    df_pff["Formula A Value"] = formula_a_value
    df_pff["Consent FPF Value"] = consent_flow_value
    df_pff = df_pff.drop(
        columns=["Spill Count", "Spill Duration (days)", "Spill Volume"]
    )
    filename = (
        f"{run['name']}-{run['id']} - Test 3 Summary.xlsx"
        if run["name"]
        else f"Run-{run['id']} - Test 3 Summary.xlsx"
    )
    df_pff.to_excel(config.test_three_outputs / filename, index=False)
    runs_tracker[str(run["id"])]["progress"]["test-3"] = "Completed!"

    for test in run["assets"][assetID]["assettests"]:
        if test == "Test 3":
            await db.assettests.update(
                where={"id": run["assets"][assetID]["assettests"][test]}, data={"status": "COMPLETED"}
            )


async def saveSummaryToDB(db, run, assetID, summary):
    """
    Helper function to save given summary data to the database.

    Args:
        db: The prisma db object.
        run: The run database information.
        summary: The summary data to be saved.
    """
    assettestid = (
        run["assets"][assetID]["assettests"]["Test 1"]
        if "Test 1" in run["assets"][assetID]["assettests"]
        else run["assets"][assetID]["assettests"]["Test 2"]
    )
    async with db.batch_() as batcher:
        print("In Batch...")
        for index, row in summary.iterrows():
            batcher.summary.create(
                data={
                    "year": str(row["Year"]),
                    "dryPerc": row["Percentage of dry days (%)"],
                    "heavyPerc": row[
                        "Percentage of year spills are allowed to start (%)"
                    ],
                    "spillPerc": row[
                        f"{run['name']} - Percentage of year spilling (%)"
                    ],
                    "unsatisfactorySpills": row[
                        f"{run['name']} - Unsatisfactory Spills"
                    ],
                    "substandardSpills": row[f"{run['name']} - Substandard Spills"],
                    "satisfactorySpills": row[f"{run['name']} - Satisfactory Spills"],
                    "totalIntensity": (
                        row["Total Rainfall (mm)"]
                        if math.isnan(row["Total Rainfall (mm)"]) == False
                        else 0.0
                    ),
                    "assetTestID": assettestid,
                }
            )
        print("Committing batch...")
        await batcher.commit()


async def saveTimeSeriesToDB(db, run, assetID, df):
    """
    Helper function to save a given time series DataFrame to the database.

    Args:
        db (Database): The primsa database object.
        run (dict): The run database information.
        df (DataFrame): The time series DataFrame to be saved.
    """
    global runs_tracker

    assettestid = (
        run["assets"][assetID]["assettests"]["Test 1"]
        if "Test 1" in run["assets"][assetID]["assettests"]
        else run["assets"][assetID]["assettests"]["Test 2"]
    )
    batch_size = 10000
    total_batches = (len(df) // batch_size) + 1

    for batch_index in range(total_batches):
        start_index = batch_index * batch_size
        end_index = min((batch_index + 1) * batch_size, len(df))
        current_batch = df.iloc[start_index:end_index]
        runs_tracker[str(run["id"])]["progress"][
            "test-1&2"
        ] = f"Saving timeseries to DB... ({round((start_index/len(df))*100.0, 1)}%)"

        async with db.batch_() as batcher:
            print("In Batch...")
            for index, row in current_batch.iterrows():
                batcher.timeseries.create(
                    data={
                        "dateTime": index,
                        "intensity": row["Intensity"],
                        "depth": row["Depth_x"],
                        "rollingDepth": row["Rolling 1hr depth"],
                        "classification": row["Classification"],
                        "spillAllowed": row["Spill_allowed?"],
                        "dayType": row["Day Type"],
                        "result": row[run["name"]],
                        "runTestID": assettestid,
                    }
                )
            print("Committing batch...")
            await batcher.commit()


async def saveSpillToDB(db, run, assetID, all_spill_classification):
    """
    Helper function to save spill event data to the database.

    Args:
        db (Database): The prisma database object.
        run (dict): The run database information.
        all_spill_classification (DataFrame): The DataFrame containing spill event data.
    """
    assettestid = (
        run["assets"][assetID]["assettests"]["Test 1"]
        if "Test 1" in run["assets"][assetID]["assettests"]
        else run["assets"][assetID]["assettests"]["Test 2"]
    )
    batch_size = 100
    total_batches = (len(all_spill_classification) // batch_size) + 1

    for batch_index in range(total_batches):
        start_index = batch_index * batch_size
        end_index = min((batch_index + 1) * batch_size, len(all_spill_classification))
        current_batch = all_spill_classification.iloc[start_index:end_index]
        print(f"Currently batching {start_index} to {end_index} values")

        async with db.batch_() as batcher:
            print("In Batch...")
            for index, row in current_batch.iterrows():
                batcher.spillevent.create(
                    data={
                        "start": row["Start of Spill (absolute)"],
                        "end": row["End of Spill (absolute)"],
                        "volume": row["Spill Volume (m3)"],
                        "maxIntensity": row[
                            "Max intensity in 24hrs preceding spill start (mm/hr)"
                        ],
                        "maxDepthInHour": row[
                            "Max depth in an hour in 24hrs preceding spill start (mm/hr)"
                        ],
                        "totalDepth": row[
                            "Total depth in 24hrs preceding spill start (mm)"
                        ],
                        "test1": row["Test 1 Status"],
                        "test2": row["Test 2 Status"],
                        "classification": row["Classification"],
                        "runTestID": assettestid,
                    }
                )
            print("Committing batch...")
            await batcher.commit()


async def saveTest3ToDB(db, run, assetID, df_pff, formula_a, consent_fpf):
    """
    Helper function to save test 3 data to the database.

    Parameters:
    - db: The prisma database object.
    - run: The run database information.
    - df_pff: The DataFrame containing the test 3 data.
    - formula_a: The formula A input.
    - consent_fpf: The consent FPF input.
    """
    for index, row in df_pff.iterrows():
        await db.testthree.create(
            data={
                "year": str(row["Year"]),
                "formulaAInput": (formula_a),
                "consentFPFInput": (consent_fpf),
                "complianceStatus": row["Compliance Status"],
                "formulaAStatus": row["Just Formula A"],
                "consentFPFStatus": row["Just Consent FPF"],
                "runTestID": run["assets"][assetID]["assettests"]["Test 3"],
            }
        )
