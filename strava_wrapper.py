from stravalib import Client
import os
import requests
import webbrowser
import time
from dotenv import load_dotenv
from flask import Flask, request
from strava_oauth import get_token

access_token = get_token()

client = Client(access_token=access_token, rate_limit_requests=True)

def download_activity_after(date):
    activities = client.get_activities(after=date)
    
    # Convert new activities to dictionary format
    return [{
        'start_date': activity.start_date.isoformat(),
        'id': activity.id
    } for activity in activities]