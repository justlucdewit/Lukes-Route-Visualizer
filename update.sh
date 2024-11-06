#!/bin/bash

python3 -c "

import sys;
sys.path.append('src');
from update_activity import update_activity
from update_routes import update_polylines, update_routes

# Make sure we have all activities stored locally in cache
update_activity(\"storage/activity_cache.yml\")
update_polylines(\"storage/polylines\")
update_routes(\"storage/routes\")

"
