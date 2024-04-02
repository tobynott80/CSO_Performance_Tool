import io
from quart import Blueprint, render_template, request, redirect, session, url_for, flash
from app.helper.database import initDB
import asyncio

import pandas as pd
from app.gn066_tests.csvHandler import csvReader, csvWriter
from app.gn066_tests import analysis
from app.gn066_tests import visualisation as vis
from app.gn066_tests.stats import timeStats, spillStats
from threading import Thread
from app.gn066_tests.tests import test3
from app.gn066_tests import config

pd.options.mode.chained_assignment = None  # default='warn'

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
    tests = []
    for test in data:
        if data[test] == "on":
            tests.append(test)
    session["tests"] = tests
    print(session)
    return redirect(url_for(f"createRun", locid=session["loc"], step=2))


@run_blueprint.route("/create/step2", methods=["POST"])
async def createRunStep2():
    """
    API route for step 2, the final step of the runs creation routine. Validates
    all user input and dispatches the job to the thread handler.

    Returns:
        A redirect response to the created run page.
    """
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
        "runids": {},
    }

    files = await request.files

    run["baselineStatsFile"] = (
        files["Baseline Stats Report"].filename
        if "Baseline Stats Report" in files
        else None
    )
    run["rainfallStatsFile"] = (
        files["rainfall-stats"].filename if "rainfall-stats" in files else None
    )
    run["spillStatsFile"] = (
        files["spill-stats"].filename if "spill-stats" in files else None
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

    print(files)

    form_data = await request.form

    formula_a_value = safe_float_conversion(form_data.get("formula-a"), default=None)
    consent_flow_value = safe_float_conversion(
        form_data.get("consent-flow"), default=None
    )

    runs_tracker[str(run["id"])] = run

    onlyOnce = False

    for test in run["tests"]:
        if test == "test-1" or test == "test-2":

            # Check if appropriate files are uploaded
            if "rainfall-stats" not in files or "spill-stats" not in files:
                await flash(
                    "Missing required files. Please upload both Rainfall Stats and Spill Stats.",
                    "error",
                )
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Check correct format
            if not files["rainfall-stats"].filename.endswith((".csv")) or not files[
                "spill-stats"
            ].filename.endswith((".xlsx")):
                await flash(
                    "Invalid file format. Please upload files the rainfall-stats as a .csv and spill-stats as a .xlsx.",
                    "error",
                )
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

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
                    await flash(
                        "Invalid Rainfall Stats file: 'P_DATETIME' column missing.",
                        "error",
                    )
                    return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            except Exception as e:
                await flash(f"Error reading Rainfall Stats file: {e}", "error")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

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
                    await flash(
                        "Missing required columns in Spill Stats file: "
                        + ", ".join(missing_columns),
                        "error",
                    )
                    return redirect(url_for(f"createRun", locid=session["loc"], step=2))
            except Exception as e:
                await flash(f"Error reading Spill Stats file: {e}", "error")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Connect Tests in DB to frontend tests
            testid = await db.tests.find_first(
                where={"name": "Test 1" if test == "test-1" else "Test 2"}
            )

            runtest = await db.runtests.create(
                data={"runID": run["id"], "testID": testid.id, "status": "PROGRESS"}
            )

            # Store RunTest ID for when running thread
            run["runids"][testid.name] = runtest.id

            # If both Test 1 & 2 selected, ensure thread is only ran once
            if onlyOnce == True:
                continue

            onlyOnce = True

            test12thread = Thread(
                target=test1and2callback,
                args=(
                    files["rainfall-stats"],
                    (files["spill-stats"], "None", run["name"]),
                    run,
                ),
            )
            test12thread.start()

        if test == "test-3":

            # Check if Baseline Stats Report is present
            if "Baseline Stats Report" not in files:
                await flash("Baseline Stats Report is required for Test 3")
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Correct format check
            if not files["Baseline Stats Report"].filename.endswith(
                (".xlsx", ".csv", ".xls")
            ):
                await flash(
                    "Invalid file format. Only '.xlsx', '.csv', and '.xls' files are supported."
                )
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Load the Excel file and checks whether sheet "Summary" exists
            try:
                df_pff = pd.read_excel(
                    files["Baseline Stats Report"].stream,
                    sheet_name="Summary",
                    header=1,
                    nrows=2,
                )
            except Exception as e:
                await flash(
                    "Error reading file, Please Input a valid Excel file. Error: "
                    + str(e)
                )
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Check if required columns are present
            required_columns = ["Peak PFF (l/s)", "Avg Initial PFF (l/s)", "Year"]
            missing_columns = [
                column for column in required_columns if column not in df_pff.columns
            ]
            if missing_columns:
                await flash("Missing required columns: " + ", ".join(missing_columns))
                return redirect(url_for(f"createRun", locid=session["loc"], step=2))

            # Connect Tests in DB to frontend tests
            testid = await db.tests.find_first(where={"name": "Test 3"})

            runtest = await db.runtests.create(
                data={"runID": run["id"], "testID": testid.id, "status": "PROGRESS"}
            )

            # Store RunTest ID for when running thread
            run["runids"][testid.name] = runtest.id
            test3thread = Thread(
                target=test3callback,
                args=(
                    formula_a_value,
                    consent_flow_value,
                    files["Baseline Stats Report"],
                    run,
                ),
            )
            test3thread.start()

    print(run)
    # Delete session data since not needed in client side
    session.pop("loc")
    session.pop("run_name")
    session.pop("run_desc")
    session.pop("tests")

    return redirect(f"/{run['locationID']}/{run['id']}")


@run_blueprint.route("/status", methods=["GET"])
async def checkStatus():
    """
    Returns the current status of the runs_tracker.

    Returns:
        The current value of the runs_tracker.
    """
    global runs_tracker
    return runs_tracker


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


def test1and2callback(rainfall_file, spills_baseline, run):
    """
    Callback function to execute tests 1 and 2.

    Args:
        rainfall_file (str): The path to the rainfall file.
        spills_baseline (str): The path to the spills baseline file.
        run (str): The run database information.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(createTests1andor2(rainfall_file, spills_baseline, run))
    loop.close()
    return


def test3callback(formula_a_value, consent_flow_value, baseline_stats_file, run):
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
        createTest3(formula_a_value, consent_flow_value, baseline_stats_file, run)
    )
    loop.close()


async def createTests1andor2(rainfall_file, spills_baseline, run):
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

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Calculating Summary Stats"

    perc_data = timeStats.time_stats(df, spills_baseline)

    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Calculating Spill Stats"

    all_spill_classification, spill_count_data = spillStats.spill_stats(
        spills_df, df, [1, 2]
    )
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Merging Dataframes"

    summary = pd.merge(perc_data, spill_count_data, on="Year")

    # Save all results to SQLite database
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Saving summary to DB"
    await saveSummaryToDB(db, run, summary)
    runs_tracker[str(run["id"])]["progress"]["test-1&2"] = "Saving spills to DB"
    await saveSpillToDB(db, run, all_spill_classification)

    for test in run["runids"]:
        if test == "Test 1" or test == "Test 2":
            await db.runtests.update(
                where={"id": run["runids"][test]}, data={"status": "COMPLETED"}
            )

    runs_tracker[str(run["id"])]["progress"][
        "test-1&2"
    ] = "Saving timeseries to DB. This may take a while."
    # Saves 300k worth of rows - can be done in background?
    await saveTimeSeriesToDB(db, run, df)

    # csvWriter.writeCSV(df, summary, all_spill_classification)


async def createTest3(formula_a_value, consent_flow_value, baseline_stats_file, run):
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
    await saveTest3ToDB(db, run, df_pff, formula_a_value, consent_flow_value)

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
    runs_tracker[str(run["id"])]["progress"]["test-3"] = "Completed! Saving to DB"

    for test in run["runids"]:
        if test == "Test 3":
            await db.runtests.update(
                where={"id": run["runids"][test]}, data={"status": "COMPLETED"}
            )


async def saveSummaryToDB(db, run, summary):
    """
    Helper function to save given summary data to the database.

    Args:
        db: The prisma db object.
        run: The run database information.
        summary: The summary data to be saved.
    """
    for index, row in summary.iterrows():
        await db.summary.create(
            data={
                "year": str(row["Year"]),
                "dryPerc": row["Percentage of dry days (%)"],
                "heavyPerc": row["Percentage of year spills are allowed to start (%)"],
                "spillPerc": row[f"{run['name']} - Percentage of year spilling (%)"],
                "unsatisfactorySpills": row[f"{run['name']} - Unsatisfactory Spills"],
                "substandardSpills": row[f"{run['name']} - Substandard Spills"],
                "satisfactorySpills": row[f"{run['name']} - Satisfactory Spills"],
                "runTestID": (
                    run["runids"]["Test 1"]
                    if "Test 1" in run["runids"]
                    else run["runids"]["Test 2"]
                ),
            }
        )


async def saveTimeSeriesToDB(db, run, df):
    """
    Helper function to save a given time series DataFrame to the database.

    Args:
        db (Database): The primsa database object.
        run (dict): The run database information.
        df (DataFrame): The time series DataFrame to be saved.
    """
    for index, row in df.iterrows():
        await db.timeseries.create(
            data={
                "dateTime": index,
                "intensity": row["Intensity"],
                "depth": row["Depth_x"],
                "rollingDepth": row["Rolling 1hr depth"],
                "classification": row["Classification"],
                "spillAllowed": row["Spill_allowed?"],
                "dayType": row["Day Type"],
                "result": row[run["name"]],
                "runTestID": (
                    run["runids"]["Test 1"]
                    if "Test 1" in run["runids"]
                    else run["runids"]["Test 2"]
                ),
            }
        )


async def saveSpillToDB(db, run, all_spill_classification):
    """
    Helper function to save spill event data to the database.

    Args:
        db (Database): The prisma database object.
        run (dict): The run database information.
        all_spill_classification (DataFrame): The DataFrame containing spill event data.
    """
    print(all_spill_classification)
    for index, row in all_spill_classification.iterrows():
        await db.spillevent.create(
            data={
                "start": row["Start of Spill (absolute)"],
                "end": row["End of Spill (absolute)"],
                "volume": row["Spill Volume (m3)"],
                "runName": run["name"],
                "maxIntensity": row[
                    "Max intensity in 24hrs preceding spill start (mm/hr)"
                ],
                "maxDepthInHour": row[
                    "Max depth in an hour in 24hrs preceding spill start (mm/hr)"
                ],
                "totalDepth": row["Total depth in 24hrs preceding spill start (mm)"],
                "test1": row["Test 1 Status"],
                "test2": row["Test 2 Status"],
                "classification": row["Classification"],
                "runTestID": (
                    run["runids"]["Test 1"]
                    if "Test 1" in run["runids"]
                    else run["runids"]["Test 2"]
                ),
            }
        )


async def saveTest3ToDB(db, run, df_pff, formula_a, consent_fpf):
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
                "runTestID": run["runids"]["Test 3"],
            }
        )
