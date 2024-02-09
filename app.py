from flask import Flask, redirect, url_for, render_template, request
from dotenv import load_dotenv
import os 
import requests


app = Flask(__name__)

load_dotenv()

# Strava API Configuration
STRAVA_CLIENT_ID = os.getenv('CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
STRAVA_REDIRECT_URI = 'http://localhost:5000/strava/callback'

# Home Page with Get Started Button
@app.route('/')
def home():
    return render_template('home.html')

# Login Page
@app.route('/login')
def login():
    return render_template('login.html')

# Strava Authentication Route
@app.route('/strava/login')
def strava_login():
    strava_auth_url = (
        f'{STRAVA_AUTH_URL}?client_id={STRAVA_CLIENT_ID}'
        f'&redirect_uri={STRAVA_REDIRECT_URI}&response_type=code&scope=read'
    )
    return redirect(strava_auth_url)

# Inside the strava_callback route
# Callback Route
@app.route('/strava/callback')
def strava_callback():
    # Extract code from query parameters
    code = request.args.get('code')

    # Exchange code for access token
    token_response = exchange_code_for_token(code)

    # Check if the token exchange was successful
    if 'access_token' in token_response:
        access_token = token_response['access_token']

        # Fetch user details
        user_details = fetch_user_details(access_token)

        # Check if user details retrieval was successful
        if user_details:
            user_name = user_details.get('firstname', 'Unknown')
            return render_template('dashboard.html', user_name=user_name)
        else:
            return 'Failed to fetch user details'
    else:
        return 'Token exchange failed'

# Function to exchange code for access token
def exchange_code_for_token(code):
    token_url = 'https://www.strava.com/api/v3/oauth/token'
    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    return response.json()

# Function to fetch user details
def fetch_user_details(access_token):
    strava_athlete_url = 'https://www.strava.com/api/v3/athlete'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(strava_athlete_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        # Print or log the response for debugging
        print(response.text)
        return None

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)
