#!/bin/bash

source .env

python3 -c "

import sys
sys.path.append('src');
from render import render_routes

points = $RENDER_POINTS_OF_INTEREST
filters = [$RENDER_FILTER]

render_routes(filters, type=\"$RENDER_TYPE\", live=False, size=($RENDER_WIDTH, $RENDER_HEIGHT), color_alg=\"$RENDER_COLOR_ALG\", background=\"$RENDER_BACKGROUND\", points=points, zoom_times=$RENDER_ZOOM, default_offset=$RENDER_OFFSET)
"
