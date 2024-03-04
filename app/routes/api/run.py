from quart import Blueprint, render_template, request, redirect, session, url_for
from datetime import date

run_blueprint = Blueprint("run", __name__)


@run_blueprint.route("/create/step1", methods=["POST"])
async def createRunStep1():
    # Use sessions to save step 1 data and then use it when submitting step 2 to create a run
    data = (await request.form).to_dict()
    if (data is None):
        return redirect("/")
    if 'loc' not in data:
        return redirect("/")
    else:
        session["loc"] = data.pop("loc")
    # If no run name given, set one with the ID from prisma? eg: Run 1
    session["run_name"] = data.pop("run_name", "Run N")
    session["run_desc"] = data.pop("run_desc", "N/A")
    session["run_date"] = data.pop("run_date", date.today())
    tests = []
    for test in data:
        if (data[test] == "on"):
            tests.append(test)
    session["tests"] = tests
    print(session)
    return redirect(url_for(f"createRun", locid=session['loc'], step=2))


@run_blueprint.route("/create/step2", methods=["GET", "POST"])
async def createRunStep2():
    return await render_template("runs/create_two.html")
