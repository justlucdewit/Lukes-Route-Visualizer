from strava_wrapper import download_activity_after
from datetime import datetime
import yaml
import os

# Function for downloading all of your strava activity locally
def update_activity(cache_file):
    print("Downloading latest strava activity...")

    # Load existing data from the YAML file if it exists
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            existing_data = yaml.safe_load(file)['activities']
            
        # Find the latest activity timestamp in the cache
        last_date = max(datetime.fromisoformat(activity['start_date']) for activity in existing_data) if existing_data else None
    else:
        existing_data = []
        last_date = None
    
    # Retrieve the latest data that we dont already have
    new_data = download_activity_after(last_date)

    if len(new_data) > 0:

        # Combine new data with existing data
        combined_data = existing_data + new_data

        # Save combined data back to YAML file
        with open(cache_file, 'w') as file:
            yaml.dump({
                "activities": combined_data
            }, file)
            
        print(f"Cached {len(new_data)} new activities!")
    else:
        print(f"Cached activities are up to date!")