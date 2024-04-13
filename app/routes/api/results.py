from typing import Optional, Tuple
from quart import Blueprint, request
from app.helper.database import initDB
import datetime


results_blueprint = Blueprint("results", __name__)


db = None


@results_blueprint.before_app_serving
async def initializeDB():
    """
    Initializes the database connection.

    This function is called before serving the application and initializes a global prisma variable to access the database.

    Returns:
        None
    """
    global db
    db = await initDB()


@results_blueprint.after_app_serving
async def closeDB():
    """
    Closes the database connection.

    This function is called after serving the application and gracefully disconnects the prisma instance.

    Returns:
        None
    """
    global db
    db = await db.disconnect()


@results_blueprint.route("/timeseries", methods=["GET"])
async def getTimeSeries():
    """
    Retrieves time series data based on the provided parameters.

    Parameters:
    - assetTestID (int): The ID of the asset test.
    - startTime (int): The start time of the time series data (in epoch time).
    - endTime (int): The end time of the time series data (in epoch time).

    Returns:
    - If no start or end time is provided, returns the entire time series data for the provided asset test ID.
    - If start and end time are provided, returns the time series data within that range for the provided asset test ID.
    """
    asset_test_ID = request.args.get("assetTestID")
    if asset_test_ID is None:
        return {"error": "No run test ID provided"}, 400

    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")

    # If no start or end time is provided, return the entire timeseries
    if start_time is None or end_time is None:
        timeseries_list = await db.timeseries.find_many(
            where={"assetTestID": int(asset_test_ID)},
            include={"TimeSeriesResult": True},
        )
        if not timeseries_list:
            return {
                "error": "No timeseries data found for the provided asset test ID"
            }, 404
        else:
            return [timeseries.dict() for timeseries in timeseries_list], 200

    # If start and end time is provided, return the timeseries within that range
    # Convert epoch time to datetime object
    start_time = datetime.datetime.fromtimestamp(int(start_time))
    end_time = datetime.datetime.fromtimestamp(int(end_time))
    timeseries_list = await db.timeseries.find_many(
        where={
            "assetTestID": int(asset_test_ID),
            "dateTime": {"gte": start_time, "lte": end_time},
        },
        order={"dateTime": "asc"},
        include={"TimeSeriesResult": True},
    )
    if not timeseries_list:
        return {
            "error": "No timeseries data found for the provided asset test ID or given time"
        }, 404
    return [timeseries.model_dump() for timeseries in timeseries_list], 200


@results_blueprint.route("/timeseries/range", methods=["GET"])
async def getTimesSeriesRange():
    """
    Retrieves the earliest and latest datetime for a given asset test ID.

    Returns:
        A dictionary containing the earliest and latest datetime in ISO format if successful.
        Otherwise, returns an error message and status code.
    """
    asset_test_ID = request.args.get("assetTestID")
    if asset_test_ID is None:
        return {"error": "No asset test ID provided"}, 400

    try:
        asset_test_ID = int(asset_test_ID)
    except ValueError:
        return {"error": "Invalid asset test ID provided"}, 400

    earliest_datetime, latest_datetime = await get_datetime_range(asset_test_ID)

    if earliest_datetime is None or latest_datetime is None:
        return {"error": "No timeseries data found for the provided asset test ID"}, 404

    return {
        "earliest_datetime": earliest_datetime.isoformat(),
        "latest_datetime": latest_datetime.isoformat(),
    }, 200


async def get_datetime_range(
    asset_test_ID: int,
) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
    """
    Helper function to retrieve the earliest and latest datetime values for a given asset test ID.

    Args:
        asset_test_ID (int): The ID of the asset test.

    Returns:
        tuple: A tuple containing the earliest and latest datetime values.
            If no datetime values are found, None is returned for both.

    """
    earliest_datetime = await db.timeseries.find_first(
        where={"assetTestID": int(asset_test_ID)},
        order={"dateTime": "asc"},
    )
    if earliest_datetime:
        earliest_datetime = earliest_datetime.dateTime

    latest_datetime = await db.timeseries.find_first(
        where={"assetTestID": int(asset_test_ID)},
        order={"dateTime": "desc"},
    )
    if latest_datetime:
        latest_datetime = latest_datetime.dateTime

    return earliest_datetime, latest_datetime
