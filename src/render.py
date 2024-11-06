import pygame
import sys
import os
import ast
import colorsys
import time
import re

def get_hue_color_from_hashed_id(route_id):
    hue = (route_id * 137.508) % 360  # Use golden angle for color variation
    lightness = 0.5  # Keep lightness constant for good visibility
    saturation = 1.0  # Full saturation for vibrant colors
    rgb = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
    return tuple(int(c * 255) for c in rgb)

def latlons_to_coords(coords, scale, offset_x, offset_y):
    return list(map(lambda coord: latlon_to_coord(coord, scale, offset_x, offset_y), coords))

def latlon_to_coord(coord, scale, offset_x, offset_y):
    (lat, lon) = coord
    return (
        int((lon - offset_x) * scale),
        int((lat - offset_y) * scale)
    )
    
def coords_to_latlons(coords, scale, offset_x, offset_y):
    return list(map(lambda x: coords_to_latlons(x, scale, offset_x, offset_y), coords))
    
def coord_to_latlon(coord, scale, offset_x, offset_y):
    (x, y) = coord
    return (
        (y / scale) + offset_y,    # Convert y back to latitude
        (x / scale) + offset_x     # Convert x back to longitude
    )
    
def get_color_from_alg(route_id, alg):
    static_rgb_match = re.match(r"^static\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$", alg)
    
    if alg == "hash":
        return get_hue_color_from_hashed_id(route_id)
    if static_rgb_match:
        r, g, b = map(int, static_rgb_match.groups())
        return (r, g, b)

def render_routes(
    filters=[],
    type="polyline",
    live=True,
    size=(800, 600),
    color_alg="hash",
    background="0,0,0",
    points=[],
    zoom_times=0,
    default_offset=(0, 0)
):
    isFiltered = len(filters) > 0

    # Function to load routes from files
    def load_routes(folder):
        routes = {}
        for filename in os.listdir(folder):
            if filename.endswith(f'.{type}'):
                route_id = int(filename.split('.')[0])  # Extract route number from filename

                if isFiltered and (not route_id in filters):
                    continue

                with open(os.path.join(folder, filename), 'r') as file:
                    coords = ast.literal_eval(file.read())
                    routes[route_id] = coords
        return routes

    # Load routes from the specified folder
    routes = load_routes(f'storage/{type}s') # Adjust the folder name as necessary

    if len(routes) == 0:
        print("No routes to display")
        return

    # Initialize Pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Set up display
    width, height = size
    surface = pygame.Surface((width, height))
    
    if live:
        window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Route Plotter")

    # Define colors for each route
    route_colors = {route_id: get_color_from_alg(route_id, color_alg) for route_id in routes.keys()}

    # Calculate scaling and offset based on min/max lat/lon
    all_coords = [point for route in routes.values() for point in route]
    min_lat = min(coord[0] for coord in all_coords)
    max_lat = max(coord[0] for coord in all_coords)
    min_lon = min(coord[1] for coord in all_coords)
    max_lon = max(coord[1] for coord in all_coords)

    # Define scaling factors (zoomed out initially)
    buffer = 0.1  # 10% buffer around the routes
    scale_x = width / ((max_lon - min_lon) * (1 + buffer))
    scale_y = height / ((max_lat - min_lat) * (1 + buffer))
    scale = min(scale_x, scale_y)
    
    # Define offsets to center the plot
    (window_top_lat, widow_right_lon) = coord_to_latlon((width, height), scale, min_lon, min_lat)
    
    offset_x = min_lon - (((widow_right_lon - min_lon) - (max_lon - min_lon)) / 2)
    offset_y = min_lat - (((window_top_lat - min_lat) - (max_lat - min_lat)) / 2)
    
    # Movement speed factor
    movement_speed = 0.01  # Adjust movement speed if necessary
    screenshot_taken = False  # Initialize screenshot flag
    zoom_factor = 0.02
    
    # Apply default zoom
    for i in range(0, zoom_times):
        scale *= (1 + zoom_factor)
        movement_speed *= (1 - zoom_factor)
        offset_x += (width / 2 / scale) * zoom_factor
        offset_y += (height / 2 / scale) * zoom_factor
    
    # Apply default offset
    offset_x += movement_speed * default_offset[0]
    offset_y -= movement_speed * default_offset[1]

    # Main loop
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
    
        # Movement controls
        if keys[pygame.K_s]:
            offset_y -= movement_speed  # Move down
        if keys[pygame.K_w]:
            offset_y += movement_speed  # Move up
        if keys[pygame.K_a]:
            offset_x -= movement_speed  # Move left
        if keys[pygame.K_d]:
            offset_x += movement_speed  # Move right

        # Zoom controls
        if keys[pygame.K_q]:  # Zoom in
            scale *= (1 - zoom_factor)
            movement_speed *= (1 + zoom_factor)
            
            # Adjust offsets to keep zooming centered
            offset_x -= (width / 2 / scale) * zoom_factor
            offset_y -= (height / 2 / scale) * zoom_factor
        if keys[pygame.K_e]:  # Zoom out
            scale *= (1 + zoom_factor)
            movement_speed *= (1 - zoom_factor)
            
            # Adjust offsets to keep zooming centered
            offset_x += (width / 2 / scale) * zoom_factor
            offset_y += (height / 2 / scale) * zoom_factor
            
        # Check for screenshot key press
        if keys[pygame.K_p]:  # Press 'P' to take a screenshot
            if not screenshot_taken:  # Check if a screenshot has already been taken
                # Create screenshots directory if it doesn't exist
                if not os.path.exists('screenshots'):
                    os.makedirs('screenshots')
                
                # Save the current display to a file
                filename = f'screenshots/map_{int(time.time())}.png'
                pygame.image.save(surface, filename)
                print(f'saved screenshot as {filename}')
                
                # Set flag to indicate a screenshot has been taken
                screenshot_taken = True
        else:
            # Reset the flag when the key is released
            screenshot_taken = False

        # Clear the screen
        surface.fill(tuple(list(map(int, background.split(',')))))  # Clear the screen with a black background

        # Draw the routes
        for route_id, coords in routes.items():
            scaled_coords = latlons_to_coords(coords, scale, offset_x, offset_y)

            # Invert the Y
            scaled_coords = list(map(lambda x: [x[0], height - x[1]], scaled_coords))

            color = route_colors[route_id]
            pygame.draw.lines(surface, color, False, scaled_coords, 2)  # Draw the route line
            
        # Draw the points
        for point in points:
            screen_coords = latlon_to_coord(point["coords"], scale, offset_x, offset_y)
            screen_coords = (screen_coords[0], height - screen_coords[1])
            pygame.draw.circle(surface, point["color"], screen_coords, point["radius"])
            
        if not live:
            # Create screenshots directory if it doesn't exist
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            
            # Save the current display to a file
            filename = f'screenshots/map_{int(time.time())}.png'
            pygame.image.save(surface, filename)
            print(f'saved map as {filename}')
            break
        
        window.blit(surface, (0, 0))

        pygame.display.flip()  # Update the display
        clock.tick(30)  # Cap the frame rate

    pygame.quit()
    sys.exit()
