import os
import yaml
from strava_wrapper import download_route_from_activity_id

def update_routes(folder):
    activity_cache_path='storage/activity_cache.yml'
    
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    
    # Load the activity cache
    with open(activity_cache_path, 'r') as cache_file:
        activity_cache = yaml.load(cache_file)["activities"]
    
    cached_count = 0

    # Go over each entry in the activity_cache
    for activity in activity_cache:
        activity_id = activity.get('id')
        
        # Define the path for the route file
        route_file_path = os.path.join(folder, f"{activity_id}.route")

        # If the route file does not exist
        if not os.path.exists(route_file_path):
            print(f"Cached route for activity {activity_id}")

            # Get the route array (route data points) for this activity
            try:
                route_array = download_route_from_activity_id(activity_id)
            except Exception as e:
                print(f"Failed to download route for activity {activity_id}: {e}")
                continue

            # Write the route array to the file
            with open(route_file_path, 'w') as route_file:
                route_file.write(str(route_array))
            
            cached_count += 1
    
    # Print how many times a route was cached
    print(f"{cached_count} new routes were cached.")