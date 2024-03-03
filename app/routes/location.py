from flask import Blueprint, request, render_template_string, render_template
from prisma.models import Location

location_blueprint = Blueprint("location", __name__)


@location_blueprint.route("/", methods=["GET", "POST"])
def location():
    if request.method == "GET":
        locations = Location.prisma().find_many()
        return {"locations": [dict(location) for location in locations]}

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
