import pygame
import sys
import os
import ast
import colorsys
import time

def render_routes():
    # Function to load routes from files
    def load_routes(folder):
        routes = {}
        for filename in os.listdir(folder):
            if filename.endswith('.route'):
                route_id = int(filename.split('.')[0])  # Extract route number from filename
                with open(os.path.join(folder, filename), 'r') as file:
                    coords = ast.literal_eval(file.read())
                    routes[route_id] = coords
        return routes

    # Load routes from the specified folder
    routes = load_routes('storage/routes')  # Adjust the folder name as necessary

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 800, 600
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Route Plotter")

    def get_hue_color(route_id):
        hue = (route_id * 137.508) % 360  # Use golden angle for color variation
        lightness = 0.5  # Keep lightness constant for good visibility
        saturation = 1.0  # Full saturation for vibrant colors
        rgb = colorsys.hls_to_rgb(hue / 360, lightness, saturation)
        return tuple(int(c * 255) for c in rgb)

    # Define colors for each route
    route_colors = {route_id: get_hue_color(route_id) for route_id in routes.keys()}

    # Scaling and translation settings
    def scale_and_translate(coords, scale, offset_x, offset_y):
        """Scales and translates coordinates to fit the window."""
        return [(int((lon - offset_x) * scale), int((lat - offset_y) * scale)) for lat, lon in coords]

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
    offset_x = min_lon
    offset_y = min_lat

    # Movement speed factor
    movement_speed = 5
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        
        # Calculate the center of the current view
        center_x = offset_x + (width / (2 * scale))
        center_y = offset_y + (height / (2 * scale))
        
        # Movement controls
        if keys[pygame.K_w]:
            offset_y -= movement_speed / scale  # Move up
        if keys[pygame.K_s]:
            offset_y += movement_speed / scale  # Move down
        if keys[pygame.K_a]:
            offset_x -= movement_speed / scale  # Move left
        if keys[pygame.K_d]:
            offset_x += movement_speed / scale  # Move right
        
        # Zoom controls
        zoom_factor = 0.005
        if keys[pygame.K_q]:  # Zoom in
            scale *= (1 - zoom_factor)
            # Adjust offsets to keep zooming centered
            offset_x -= (width / 2 / scale) * zoom_factor
            offset_y -= (height / 2 / scale) * zoom_factor
        if keys[pygame.K_e]:  # Zoom out
            scale *= (1 + zoom_factor)
            # Adjust offsets to keep zooming centered
            offset_x += (width / 2 / scale) * zoom_factor
            offset_y += (height / 2 / scale) * zoom_factor
            
        # Check for screenshot key press
        if keys[pygame.K_p]:  # Press 'P' to take a screenshot
            if not screenshot_taken:  # Check if a screenshot has already been taken
                # Create screenshots directory if it doesn't exist
                if not os.path.exists('screenshots'):
                    os.makedirs('screenshots')
                
                # Generate a Unix timestamp for the filename
                timestamp = int(time.time())  # Get the current Unix timestamp
                screenshot_path = f'screenshots/screenshot_{timestamp}.png'
                
                # Save the current display to a file
                pygame.image.save(window, screenshot_path)
                print(f'Screenshot saved as: {screenshot_path}')
                
                # Set flag to indicate a screenshot has been taken
                screenshot_taken = True
        else:
            # Reset the flag when the key is released
            screenshot_taken = False

        # Clear the screen
        window.fill((0, 0, 0))  # Clear the screen with a black background

        # Draw the routes
        for route_id, coords in routes.items():
            scaled_coords = scale_and_translate(coords, scale, offset_x, offset_y)
            color = route_colors[route_id]
            pygame.draw.lines(window, color, False, scaled_coords, 2)  # Draw the route line

        pygame.display.flip()  # Update the display

    # Clean up
    pygame.quit()
    sys.exit()
