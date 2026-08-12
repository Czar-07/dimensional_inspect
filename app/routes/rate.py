from flask import Blueprint, render_template


rate_page = Blueprint(
    "rate_page",
    __name__,
)


@rate_page.route("/")
def index():
    return render_template("dashboard.html")


@rate_page.route("/rate")
def rate():
    return render_template("dashboard.html")


@rate_page.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@rate_page.route("/report")
def report():
    return render_template("report.html")


@rate_page.route("/history")
def history():
    return render_template("history.html")
