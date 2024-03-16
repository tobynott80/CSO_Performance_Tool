from quart import Blueprint, request
from app.helper.database import initDB
import datetime


results_blueprint = Blueprint("results", __name__)


db = None


@results_blueprint.before_app_serving
async def initializeDB():
    global db
    db = await initDB()


@results_blueprint.route("/timeseries", methods=["GET"])
async def getTimeSeries():
    run_test_ID = request.args.get("runTestID")
    if run_test_ID is None:
        return {"error": "No run test ID provided"}, 400

    start_time = request.args.get("startTime")
    end_time = request.args.get("endTime")

    # If no start or end time is provided, return the entire timeseries
    if start_time is None or end_time is None:
        timeseries_list = await db.timeseries.find_many(
            where={"runTestID": int(run_test_ID)}
        )
        if not timeseries_list:
            return {
                "error": "No timeseries data found for the provided run test ID"
            }, 404
        else:
            return [timeseries.dict() for timeseries in timeseries_list], 200

    # If start and end time is provided, return the timeseries within that range
    # Convert epoch time to datetime object
    start_time = datetime.datetime.fromtimestamp(int(start_time))
    end_time = datetime.datetime.fromtimestamp(int(end_time))
    timeseries_list = await db.timeseries.find_many(
        where={
            "runTestID": int(run_test_ID),
            "dateTime": {"gte": start_time, "lte": end_time},
        },
        order={"dateTime": "asc"},
    )
    if not timeseries_list:
        return {
            "error": "No timeseries data found for the provided run test ID or given time"
        }, 404
    return [timeseries.model_dump() for timeseries in timeseries_list], 200
