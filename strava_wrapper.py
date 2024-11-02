from stravalib import Client
import os
import requests
import webbrowser
import time
import polyline
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
    
def download_route_from_activity_id(activity_id):
    activity = client.get_activity(activity_id)
    if activity.map and activity.map.summary_polyline:
        route_coordinates = polyline.decode(activity.map.summary_polyline)
        return route_coordinates
    else:
        return None