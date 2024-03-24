from flask import Blueprint, redirect, url_for, session, request
import requests
from dotenv import load_dotenv
import os

auth_bp = Blueprint("auth", __name__)

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

@auth_bp.route("/login")
def login():
    # Check if user is already authenticated
    if 'access_token' in session:
        return redirect(url_for("dashboard.dashboard"))
    
    # Define the desired scope
    scope = "activity:read_all,read_all"

    # Redirect user to Strava's authorization page with the defined scope
    redirect_url = f"{STRAVA_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}"
    return redirect_url

@auth_bp.route("/strava/auth", methods=['GET', 'POST'])
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
        return redirect(url_for("dashboard.dashboard", code=auth_code))
    else:
        return "Failed to authenticate with Strava"
