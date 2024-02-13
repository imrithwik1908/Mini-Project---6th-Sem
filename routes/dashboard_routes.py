from flask import Blueprint, render_template, redirect, url_for, session
import requests
from .auth_routes import API_URL

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for("auth.login"))

    # Retrieve user data from Strava API
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{API_URL}/athlete", headers=headers)
    if response.status_code == 200:
        user_name = response.json()["firstname"]
        return render_template("dashboard.html", user_name=user_name)
    else:
        return "Failed to fetch user details"
