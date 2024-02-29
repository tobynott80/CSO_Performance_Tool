from flask import Blueprint, request
from prisma.models import Location

location_blueprint = Blueprint("location", __name__)

@location_blueprint.route("/", methods=["POST"])
def location():
    if request.method == "POST":
        data = request.json
        if data is None:
            return

        name = data.get("name")

        if name is None:
            return {"error": "Name is required"}

        location = Location.prisma().create(
            data={
                "name": name,
            }
        )
        return dict(location)
