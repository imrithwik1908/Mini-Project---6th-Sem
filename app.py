from flask import Flask, redirect, url_for, render_template, session, request
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = "supersekrit"

# Load environment variables
load_dotenv()

# Strava OAuth settings
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/strava/auth'

# Strava API endpoints
STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
TOKEN_URL = 'https://www.strava.com/oauth/token'
API_URL = 'https://www.strava.com/api/v3'

# Initialize session variable to track login status
@app.before_request
def before_request():
    session.permanent = True

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    # Check if user is already authenticated
    if 'access_token' in session:
        # Check if the access token is valid by attempting to fetch user data
        access_token = session.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f"{API_URL}/athlete", headers=headers)
        if response.status_code == 200:
            # User is already authenticated and access token is valid, redirect to dashboard
            return redirect(url_for("dashboard"))
        else:
            # Access token is invalid or expired, clear session and proceed with login
            session.clear()

    # Define the desired scope
    scope = "activity:read_all,read_all"

    # Redirect user to Strava's authorization page with the defined scope
    return redirect(f"{STRAVA_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}")



@app.route("/strava/auth", methods=['GET', 'POST'])
def strava_auth():
    if request.method == 'GET':
        # Retrieve authorization code from query parameters
        auth_code = request.args.get('code')
    elif request.method == 'POST':
        # Retrieve authorization code from form data
        auth_code = request.form.get('code')
    
    # Exchange authorization code for access token
    token_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=token_params)
    if response.status_code == 200:
        print(response.json())
        access_token = response.json()['access_token']
        # print(response.json()['refresh_token'])
        # Store access token in session
        session['access_token'] = access_token
        return redirect(url_for("dashboard", code=auth_code))
    else:
        return "Failed to authenticate with Strava"


@app.route("/dashboard")
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
        return "Failed to fetch user details"


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
    app.run(debug=True)