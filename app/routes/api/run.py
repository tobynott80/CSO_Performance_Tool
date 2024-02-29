from flask import Blueprint, request, render_template_string, render_template
from prisma.models import Runs

run_blueprint = Blueprint("run", __name__)

# Create
@run_blueprint.route("/create", methods=["GET", "POST"])
def createRun():
    return render_template("runs/create.html")
