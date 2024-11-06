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
        'id': activity.id,
        'moving_time': activity.moving_time,
        'distance': activity.distance,
        'average_speed': activity.average_speed,
        'type': activity.workout_type
    } for activity in activities]
    
def download_polyline_from_activity_id(activity_id):
    activity = client.get_activity(activity_id)
    if activity.map and activity.map.summary_polyline:
        route_coordinates = polyline.decode(activity.map.summary_polyline)
        return route_coordinates
    else:
        return None
    
def download_route_from_activity_id(activity_id, resolution):
    """
    Downloads the high-resolution route from a given Strava activity ID.
    
    Parameters:
    - activity_id (int): The Strava activity ID
    - resolution (string: low | medium | high)
    
    Returns:
    - list: A list of (latitude, longitude) tuples if route exists, otherwise None.
    """
    try:
        # Attempt to retrieve the high-resolution lat/lng stream for the activity
        streams = client.get_activity_streams(activity_id, types=['latlng'], resolution=resolution)

        # Check if 'latlng' data is available in the streams
        if 'latlng' in streams:
            route_coordinates = streams['latlng'].data  # Returns a list of [lat, lng] pairs
            return route_coordinates
        else:
            print("No lat/lng data found for this activity.")
            return None
    except Exception as e:
        print(f"An error occurred while fetching the activity: {e}")
        return None