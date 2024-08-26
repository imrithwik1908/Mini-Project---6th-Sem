# api.py :

from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Strava OAuth settings
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'https://localhost'
STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
TOKEN_URL = 'https://www.strava.com/oauth/token'
API_URL = 'https://www.strava.com/api/v3'

@app.route("/authorize")
def authorize():
    """Redirect user to the Strava Authorization page"""
    # Define the desired scope
    scope = "activity:read_all,read_all" 
    auth_url = f"{STRAVA_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}"
    return jsonify({"authorization_url": auth_url})

@app.route("/strava/auth", methods=['POST'])
def strava_auth():
    """Exchange authorization code for access token"""
    auth_code = request.json.get('code')

    token_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code' 
    }
    response = requests.post(TOKEN_URL, data=token_params)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return jsonify({"access_token": access_token})
    else:
        return jsonify({"error": "Failed to authenticate with Strava"}), response.status_code
    
@app.route("/refresh_token", methods=['POST'])
def refresh_token():
    """Refresh the access token"""
    refresh_token = request.json.get('refresh_token')
    token_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(TOKEN_URL, data=token_params)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return jsonify({"access_token": access_token})
    else:
        return jsonify({"error": "Failed to refresh token"}), response.status_code

@app.route("/revoke_token", methods=['POST'])
def revoke_token():
    """Revoke the access token"""
    access_token = request.json.get('access_token')
    revoke_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'access_token': access_token
    }
    response = requests.post('https://www.strava.com/oauth/deauthorize', data=revoke_params)
    if response.status_code == 200:
        return jsonify({"message": "Access token revoked successfully"})
    else:
        return jsonify({"error": "Failed to revoke access token"}), response.status_code


@app.route("/activities", methods=['POST', 'GET'])
def get_activities():
    """Get activities from Strava"""
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token not provided"}), 400

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{API_URL}/athlete/activities", headers=headers)
    if response.status_code == 200:
        activities = response.json()
        return jsonify(activities)
    else:
        return jsonify({"error": "Failed to fetch activities from Strava"}), response.status_code


if __name__ == "__main__":
    app.run(debug=True) 