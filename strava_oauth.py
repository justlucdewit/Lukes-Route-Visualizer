import multiprocessing
import subprocess
import requests
import json
import time
import os

from flask import Flask, redirect, request
from dotenv import load_dotenv
from stravalib import Client
import threading

load_dotenv()

class StravaOAuth:
    def __init__(self, token_file):
        # Strava credentials from .env file
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.token_file = token_file

        # Create a Flask app for handling the redirect and run it
        self.app = Flask(__name__)
        
        @self.app.route('/test')
        def test():
            return "test"

        @self.app.route('/login')
        def login():
            # Redirect to Strava's authorization page
            auth_url = (
                f'https://www.strava.com/oauth/authorize?client_id={self.client_id}'
                f'&response_type=code&redirect_uri={self.redirect_uri}'
                '&approval_prompt=force&scope=read,activity:read'
            )
            
            return redirect(auth_url)

        @self.app.route('/callback')
        def callback():
            # Handle the callback from Strava
            code = request.args.get('code')

            # Exchange authorization code for access token
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
            }
            
            response = requests.post('https://www.strava.com/oauth/token', data=token_data)

            if response.status_code == 200:
                self.save_access_token(response.json())
                return 'Login successful! You can close this window.'
            else:
                return f'Error obtaining access token: {response.content}'
            
    def run_flask_app(self):
        with open(os.devnull, 'w') as fnull:
            self.app.run(port=5000, use_reloader=False, host='0.0.0.0', debug=False)
        
    def save_access_token(self, token):
            with open(self.token_file, 'w') as f:
                json.dump(token, f, indent=4)

def is_token_valid(token_info):
    """Check if the access token is valid by making a test API call."""
    access_token = token_info.get('access_token')
    if not access_token:
        return False

    # Make a simple API call to check token validity
    response = requests.get('https://www.strava.com/api/v3/athlete', headers={'Authorization': f'Bearer {access_token}'})
    
    # If the response status is 200, the token is valid
    return response.status_code == 200

saved_token = None

def get_token():
    global saved_token
    
    if saved_token:
        return saved_token
    
    token_file = os.getenv('TOKEN_FILE')
    
    # Check if the token file already exists
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_info = json.load(f)
            # Validate the access token
            if is_token_valid(token_info):
                athlete = token_info.get('athlete', {})
                print(f"Logged in as '{athlete.get('firstname', 'unknown')} {athlete.get('lastname', 'unknown')}'")
                saved_token = token_info['access_token']
                return token_info['access_token']
            
    # If no valid token, start the Flask server in a new process
    strava_auth = StravaOAuth(token_file)

    # Redirect stdout and stderr to suppress output
    server_process = subprocess.Popen(
        ['python3', '-c', f'import {strava_auth.__module__}; {strava_auth.__module__}.StravaOAuth("{token_file}").run_flask_app()'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for the user to login and obtain the token
    print("Please log in by visiting the following URL:")
    print(f"http://localhost:5000/login")
    
    # Keep checking for the token
    while not os.path.exists(token_file):
        time.sleep(1)  # Check every second
        
    server_process.terminate()
        
    # After the token is saved, read it and confirm
    with open(token_file, 'r') as f:
        token_info = json.load(f)
        athlete = token_info.get('athlete', {})
        print(f"Logged in as '{athlete.get('firstname', 'unknown')} {athlete.get('lastname', 'unknown')}'")
        saved_token = token_info['access_token']
        return token_info['access_token']
