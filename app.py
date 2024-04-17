from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, session, request
import requests
from dotenv import load_dotenv
import os
import humanize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_database import Base, User, Activity, Challenge, Leadership, Comment, Share

app = Flask(__name__)
app.secret_key = "supersekrit"

# Load environment variables
load_dotenv()

# Database engine
engine = create_engine('sqlite:///my_database1.db')
Base.metadata.bind = engine

# Rename the SQLAlchemy session object to avoid conflicts
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Define a custom Jinja filter for formatting datetime
@app.template_filter('format_datetime')
def format_datetime(dt):
    # Parse the datetime string into a datetime object
    dt_obj = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')
    # Format the datetime object into the desired format
    formatted_dt = dt_obj.strftime('%d %B %Y, %I:%M:%S %p')
    return formatted_dt

# Define a custom Jinja filter for formatting timedelta
@app.template_filter('format_timedelta')
def format_timedelta(seconds):
    # Convert seconds to timedelta object
    td = timedelta(seconds=seconds)
    # Format timedelta using humanize library
    return humanize.precisedelta(td)

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
    if 'access_token' in session:
        # Check if the access token is valid
        access_token = session.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f"{API_URL}/athlete", headers=headers)
        if response.status_code == 200:
            # User is already authenticated and access token is valid, redirect to dashboard
            return redirect(url_for("dashboard"))

    # User is not logged in or access token is invalid, render the home page with login button
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
        access_token = response.json().get('access_token')

        # Fetch user data from Strava API
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f"{API_URL}/athlete/activities", headers=headers)
        if response.status_code == 200:
            activities = response.json()

            # Add each activity to the database
            for activity in activities:
                name = activity.get('name')
                dist = activity.get('distance')
                moving_time = activity.get('moving_time')
                start_date = activity.get('start_date')
                add_activity_to_database(name, dist, moving_time, start_date)

            # Store the access token in session
            session['access_token'] = access_token

            # Redirect to the dashboard
            return redirect(url_for("dashboard"))
        else:
            return "Failed to fetch user activities from Strava API"
    else:
        return "Failed to authenticate with Strava"



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

        # Filter activities based on start date if provided
        start_date_input = request.form.get('start_date')
        if start_date_input:
            # Convert input date to format matching Strava's start_date
            try:
                start_date = datetime.strptime(start_date_input, '%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
                return "Invalid date format. Please use DD-MM-YYYY format."

            filtered_activities = []
            for activity in activities:
                activity_start_date = activity['start_date'][:10]  # Extract date part
                if start_date == activity_start_date:
                    filtered_activities.append(activity)
            activities = filtered_activities
 
        return render_template("dashboard.html", user_name=user_name, activities=activities, format_datetime=format_datetime)
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

# Function to add activity data to the database
def add_activity_to_database(name, dist, moving_time, start_date):
    try:
        # Convert start_date string to Python datetime object
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')

        # Create a new Activity object with the provided data
        new_activity = Activity(
            name=name,
            dist=dist,
            moving_time=moving_time,
            start_date=start_date_dt,
        )
        db_session.add(new_activity)
        db_session.commit()
        print("Activity data added successfully.")
    except Exception as e:
        # Rollback the transaction if an error occurs
        db_session.rollback()
        print(f"Error occurred while adding activity data: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True) 
