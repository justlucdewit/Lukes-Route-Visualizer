#!/usr/bin/env python3

from update_activity import update_activity
from update_routes import update_routes
from render import render_routes

# Make sure we have all activities stored locally in cache
update_activity("storage/activity_cache.yml")

# Make sure we have all routes stored locally in cache
update_routes("storage/routes")

# Show the window to render the routes
render_routes()