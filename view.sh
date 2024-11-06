#!/bin/bash

python3 -c "

import sys
sys.path.append('src');
from render import render_routes
filters = []
if len(sys.argv) > 1:
    filters = list(map(int, sys.argv[1].split(\",\")))

render_routes(filters, type=\"polyline\", live=True, size=(800, 600), color_alg=\"hash\")

"
