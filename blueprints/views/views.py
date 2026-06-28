"""Server-rendered pages. Each screen is its own template under templates/."""
from functools import wraps

from extensions import (
    Blueprint, render_template, current_user_id, current_role,
)
from flask import redirect, url_for, send_from_directory, current_app, abort

viewsBp = Blueprint("views", __name__)


def page_roles(*roles):
    """Page-level access guard.

    Unlike the API's role_required (which aborts with JSON 401/403), this
    redirects so users land on a sensible page: anonymous -> login, wrong
    role -> dashboard. Keeps the cosmetic nav hiding in app.js honest by
    enforcing the same data-roles on the server.
    """
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user_id():
                return redirect(url_for("views.login"))
            if current_role() not in roles:
                return redirect(url_for("views.dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


@viewsBp.get("/")
def login():
    return render_template("login.html")

@viewsBp.get("/signup")
def signup():
    return render_template("signup.html")

@viewsBp.get("/dashboard")
@page_roles("student", "staff", "manager", "admin")
def dashboard():
    return render_template("dashboard.html")

@viewsBp.get("/search")
@page_roles("student", "staff")
def search():
    return render_template("search.html")

@viewsBp.get("/resource")
@page_roles("manager", "admin")
def resource():
    return render_template("resource.html")

@viewsBp.get("/bookings")
@page_roles("student", "staff")
def bookings():
    return render_template("bookings.html")


@viewsBp.get("/equipment")
@page_roles("staff", "manager", "admin")
def equipment():
    return render_template("equipment.html")


@viewsBp.get("/approvals")
@page_roles("manager", "admin")
def approvals():
    return render_template("approvals.html")

@viewsBp.get("/equipment/manage")
@page_roles("manager", "admin")
def equipment_manage():
    return render_template("equipment_manage.html")

@viewsBp.get("/profile")
@page_roles("student", "staff", "manager", "admin")
def profile():
    return render_template("profile.html")

@viewsBp.get("/maintenance")
def maintenance():
    return render_template("maintenance.html")

@viewsBp.get("/report-issue")
@page_roles("student", "staff")
def report_issue():
    return render_template("report_issue.html")

@viewsBp.get("/view-reports")
@page_roles("manager", "admin")
def view_reports():
    return render_template("view_reports.html")

@viewsBp.get("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve an uploaded booking document / issue image to signed-in users."""
    if not current_user_id():
        abort(404)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
