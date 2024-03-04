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
