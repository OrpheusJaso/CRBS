"""Server-rendered pages. Each screen is its own template under templates/."""
from extensions import Blueprint, render_template

viewsBp = Blueprint("views", __name__)


@viewsBp.get("/")
def login():
    return render_template("login.html")


@viewsBp.get("/signup")
def signup():
    return render_template("signup.html")


@viewsBp.get("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@viewsBp.get("/search")
def search():
    return render_template("search.html")


@viewsBp.get("/bookings")
def bookings():
    return render_template("bookings.html")


@viewsBp.get("/equipment")
def equipment():
    return render_template("equipment.html")


@viewsBp.get("/approvals")
def approvals():
    return render_template("approvals.html")


@viewsBp.get("/profile")
def profile():
    return render_template("profile.html")
