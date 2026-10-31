
from flask import Flask, render_template, request
import logging
from automation import run_employee_automation

app = Flask(__name__)

# Configure application logging
logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.route("/")
def home():
    return render_template("index.html", result=None)


@app.route("/run-automation", methods=["POST"])
def run_automation():

    # Get login credentials
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Get employee details
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    employee_id = request.form.get("employee_id", "").strip()

    # Validate form inputs
    if not all([username, password, first_name, last_name, employee_id]):
        return render_template("index.html", result={
            "success": False,
            "message": "Please fill in all required fields."
        })

    logging.info("Automation request received from dashboard.")

    try:
        result = run_employee_automation(
            username,
            password,
            first_name,
            last_name,
            employee_id
        )

        return render_template("index.html", result=result)

    except Exception as e:
        logging.exception("Automation failed.")

        return render_template("index.html", result={
            "success": False,
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )
