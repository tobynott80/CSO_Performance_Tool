from quart import Blueprint, render_template

run_blueprint = Blueprint("run", __name__)

# Create
@run_blueprint.route("/create", methods=["GET", "POST"])
async def createRun():
    return await render_template("runs/create.html")
