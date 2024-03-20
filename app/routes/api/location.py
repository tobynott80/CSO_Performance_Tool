from quart import Blueprint, request
from app.helper.database import initDB

location_blueprint = Blueprint("location", __name__)

db = None


@location_blueprint.before_app_serving
async def initializeDB():
    global db
    db = await initDB()


@location_blueprint.route("/", methods=["POST"])
async def location():
    data = await request.get_json()
    if data is None:
        return
    name = data["name"]
    if name == None:
        return {"error": "Name is required"}
    location = await db.location.create(
        data={
            "name": name,
        }
    )
    return dict(location)


@location_blueprint.route("<int:locid>", methods=["DELETE"])
async def delete_location(locid):
    try:
        # Delete the location from the database
        await db.location.delete(where={"id": locid})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500
