from quart import Blueprint, request, send_file, abort
from app.helper.database import initDB
import os
import app.gn066_tests.config as config
import pandas as pd

download_blueprint = Blueprint("download", __name__)

db = None


@download_blueprint.before_app_serving
async def initializeDB():
    """
    Initializes the database connection.

    This function is called before serving the application and initializes a global prisma variable to access the database.

    Returns:
        None
    """
    global db
    db = await initDB()


@download_blueprint.after_app_serving
async def closeDB():
    """
    Closes the database connection.

    This function is called after serving the application and gracefully disconnects the prisma instance.

    Returns:
        None
    """
    global db
    db = await db.disconnect()


@download_blueprint.route("/test3/<filename>")
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


@download_blueprint.route("/dry_day/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_dry_day(location_id, run_id,asset_id):
    # Fetch the Dry Day results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {"Year": summary.year, "Percentage": summary.dryPerc}
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Dry_Day_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Dry Day Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/unsatisfactory_spills/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_unsatisfactory_spills(location_id, run_id,asset_id):
    # Fetch the Unsatisfactory Spills results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {
                "Year": summary.year,
                "Unsatisfactory Spills": summary.unsatisfactorySpills,
            }
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Unsatisfactory_Spills_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Unsatisfactory Spills Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/substandard_spills/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_substandard_spills(location_id, run_id, asset_id):
    # Fetch the Substandard Spills results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {"Year": summary.year, "Substandard Spills": summary.substandardSpills}
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Substandard_Spills_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Substandard Spills Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/heavy_perc/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_heavy_perc(location_id, run_id, asset_id):
    # Fetch the Heavy Perc results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    if not tests.assetTests:

        tests = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
            },
        )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {
                "Year": summary.year,
                "Percentage of year spills are allowed to start (%)": summary.heavyPerc,
            }
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Allowed_Spill_Start_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Allowed Spill Start Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/spill_perc/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_spill_perc(location_id, run_id, asset_id):
    # Fetch the Spill Perc results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    if not tests.assetTests:

        tests = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
            },
        )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {"Year": summary.year, "Percentage of year spilling (%)": summary.spillPerc}
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Year_Spilling_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Year Spilling Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/storm_overflow/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_storm_overflow(location_id, run_id, asset_id):
    # Fetch the Storm Overflow results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    if not tests.assetTests:

        tests = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
            },
        )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {
                "Year": summary.year,
                "Substandard Spills": summary.substandardSpills,
                "Satisfactory Spills": summary.satisfactorySpills,
            }
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Storm_Overflow_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Storm Overflow Results")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404


@download_blueprint.route("/dry_day_discharges/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_dry_day_discharges(location_id, run_id, asset_id):
    # Fetch the Dry Day Discharges(test 1) results from the database
    location = await db.location.find_first(where={"id": location_id})
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    # Convert the data to a DataFrame
    if tests and tests.assetTests[0].summary:
        data = [
            {
                "Year": summary.year,
                "Dry Day Percentage": summary.dryPerc,
                "Unsatisfactory Spills": summary.unsatisfactorySpills,
                "Substandard Spills": summary.substandardSpills,
                "Satisfactory Spills": summary.satisfactorySpills,
            }
            for summary in tests.assetTests[0].summary
        ]
        df = pd.DataFrame(data)

        # Define the filename and path
        filename = f"Dry_Day_Discharges(test 1)_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)

        # Export to Excel
        df.to_excel(filepath, index=False, sheet_name="Dry Day Discharges(test 1)")

        # Send the file for download
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No summary data available for this run", 404


@download_blueprint.route("/heavy_rainfall_spills/<int:location_id>/<int:run_id>/<int:asset_id>")
async def download_heavy_rainfall_spills(location_id, run_id, asset_id):
    # Fetch the location
    location = await db.location.find_first(where={"id": location_id})
    if not location:
        print("Location not found")
        return "Location not found", 404

    # fetching Test 1 data
    tests = await db.tests.find_first(
        where={"name": "Test 1"},
        include={
            "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
        },
    )

    # If no Test 1 data, fetch Test 2 data
    if not tests or not tests.assetTests:
        tests = await db.tests.find_first(
            where={"name": "Test 2"},
            include={
                "assetTests": {"where": {"assetID": asset_id}, "include": {"summary": True}},
            },
        )

    # Prepare data for DataFrame
    if tests and tests.assetTests and tests.assetTests[0].summary:
        test_name = tests.name  # This will be either "Test 1" or "Test 2"
        data = []
        for summary in tests.assetTests[0].summary:
            row = {
                "Year": summary.year,
                "Percentage of year spills are allowed to start (%)": summary.heavyPerc,
                "Percentage of year spilling (%)": summary.spillPerc,
            }
            # Include additional columns if Test 1 data is being used
            if test_name == "Test 1":
                row["Substandard Spills"] = summary.substandardSpills
                row["Satisfactory Spills"] = summary.satisfactorySpills
            data.append(row)

        # Convert to DataFrame and export to Excel
        df = pd.DataFrame(data)
        filename = f"Heavy_Rainfall_Spills_Results_{location.name}_{run_id}.xlsx"
        filepath = os.path.join(config.outfolder, filename)
        df.to_excel(filepath, index=False, sheet_name="Heavy Rainfall Spills")
        return await send_file(
            filepath, attachment_filename=filename, as_attachment=True
        )

    return "No data available for this run", 404
