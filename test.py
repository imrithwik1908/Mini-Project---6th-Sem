from flask import Flask, redirect, url_for, render_template, session, request
from strava_api.api import authorize, strava_auth, refresh_token, revoke_token, get_activities
from strava_api import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, STRAVA_AUTH_URL, API_URL
import os
from dotenv import load_dotenv
import requests


app = Flask(__name__)
app.secret_key = "supersekrit"

# Load environment variables
load_dotenv()

# Initialize session variable to track login status
@app.before_request
def before_request(): 
    session.permanent = True

@app.route("/")
def home():
    if 'access_token' in session:
        # Check if the access token is valid
        return redirect(url_for("dashboard"))

    # User is not logged in or access token is invalid, render the home page with login button
    return render_template("home.html")


@app.route("/login")
def login():
    # Define the desired scope
    scope = "activity:read_all,read_all" 

    # Redirect user to Strava's authorization page with the defined scope
    return redirect(f"{STRAVA_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}")

@app.route("/strava/auth", methods=['GET', 'POST'])
def strava_auth_route():
    return strava_auth()

@app.route("/refresh_token", methods=['POST'])
def refresh_token_route():
    return refresh_token()

@app.route("/revoke_token", methods=['POST'])
def revoke_token_route():
    return revoke_token()

@app.route("/activities", methods=['POST', 'GET'])
def get_activities_route():
    return get_activities()


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for("login"))

    # Retrieve user data from Strava API
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{API_URL}/athlete", headers=headers)
    if response.status_code == 200:
        user_name = response.json()["firstname"]

        # Fetch activities
        activities_response = requests.get(f"{API_URL}/athlete/activities", headers=headers)
        if activities_response.status_code == 200:
            activities = activities_response.json()
        else:
            activities = [] 

        return render_template("dashboard.html", user_name=user_name, activities=activities)
    else:
        # Access might be revoked, display message and redirect after a delay
        return render_template("access_revoked.html")


@app.route("/logout")
def logout(): 
    access_token = session.get('access_token')
    if access_token:
        # Revoke access token
        revoke_params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'access_token': access_token
        }
        revoke_response = requests.post('https://www.strava.com/oauth/deauthorize', data=revoke_params)
        if revoke_response.status_code != 200:
            return "Failed to revoke access token"

    # Clear session
    session.clear()
    # Redirect user to home page after logout
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
