from quart import Blueprint, request
from app.helper.database import initDB

location_blueprint = Blueprint("location", __name__)

db = None


@location_blueprint.before_app_serving
async def initializeDB():
    """
    Initializes the database connection.

    This function is called before serving the application and initializes a global prisma variable to access the database.

    Returns:
        None
    """
    global db
    db = await initDB()


@location_blueprint.route("/", methods=["POST"])
async def location():
    """
    Create a new location in the database.

    This function expects a JSON payload containing the name of the location.
    It creates a new location record in the database with the provided name.

    Returns:
        A dictionary representing the created location database entry.

    Example JSON payload:
        {
            "name": "New Location"
        }
    """
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
    """
    Delete a location from the database.

    Args:
        locid (int): The ID of the location to be deleted.

    Returns:
        dict: A dictionary indicating the success of the operation.
            If the deletion is successful, the dictionary will have a "success" key
            with a value of True. If an error occurs, the dictionary will have a "success" key
            with a value of False, and an "error" key with a description of the error.
    """
    try:
        # Delete the location from the database
        await db.location.delete(where={"id": locid})
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500
