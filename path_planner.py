import numpy as np
import math
from shapely.geometry import Polygon, Point, LineString

class PathPlanner:
    def __init__(self, resolution=1):
        self.resolution = resolution  # Grid resolution in meters
    
    # A* Path Planning for Dynamic Obstacle Avoidance
    def a_star(start, goal, obstacles, resolution=1):
        """Finds shortest path using A* algorithm for lat/lon."""
        open_list = [start]
        closed_list = []
        parent = {}

        def heuristic(a, b):
            # Haversine distance for lat/lon
            R = 6371000  # Earth radius in meters
            lat1, lon1 = a
            lat2, lon2 = b
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c  # distance in meters

        while open_list:
            current = min(open_list, key=lambda x: heuristic(x, goal))
            if current == goal:
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                return path[::-1]  # Return path in reverse order

            open_list.remove(current)
            closed_list.append(current)

            for dx, dy in [(0, resolution), (0, -resolution), (resolution, 0), (-resolution, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in obstacles or neighbor in closed_list:
                    continue
                if neighbor not in open_list:
                    open_list.append(neighbor)
                    parent[neighbor] = current

        return []  # No path found
    

    def boustrophedon_coverage(boundary, step_size=0.0002):
        polygon = boundary['polygon']
        lat_min, lat_max = boundary['ymin'], boundary['ymax']
        lon_min, lon_max = boundary['xmin'], boundary['xmax']
    
        path = []
        direction = 1  # Left to right: 1, Right to left: -1
    
        for lat in np.arange(lat_min, lat_max, step_size):
            line = LineString([(lon_min, lat), (lon_max, lat)])
            intersection = polygon.intersection(line)
    
            # Handle multiple segments (e.g., concave polygons)
            segments = []
            if intersection.is_empty:
                continue
            elif intersection.geom_type == 'LineString':
                segments = [intersection]
            elif intersection.geom_type == 'MultiLineString':
                segments = list(intersection)
    
        # Extract segment endpoints as path
            row_path = []
            for seg in segments:
                x1, y1, x2, y2 = *seg.coords[0], *seg.coords[-1]
                p1, p2 = (y1, x1), (y2, x2)  # (lat, lon)
                if direction == 1:
                    row_path.extend([p1, p2])
                else:
                    row_path.extend([p2, p1])
    
            if row_path:
                path.extend(row_path)
                direction *= -1
    
        return path

    
    def construct_boundary(coord_list):
        """
        Constructs a structured boundary representation from a list of (x, y) coordinate tuples.
    
        Args:
            coord_list (list of tuples): List of (x, y) coordinates defining the boundary.
    
        Returns:
            dict: A dictionary containing the boundary polygon and min/max values.
        """
        if len(coord_list) < 3:
            raise ValueError("Boundary must have at least three points to form a valid polygon")
    
        polygon = Polygon(coord_list)  # Create a polygon from the given vertices
    
        boundary = {
            'polygon': polygon,  # Store the actual polygon
            'xmin': min(p[0] for p in coord_list),
            'xmax': max(p[0] for p in coord_list),
            'ymin': min(p[1] for p in coord_list),
            'ymax': max(p[1] for p in coord_list),
            'vertices': coord_list  # Preserve original boundary points
        }
    
        return boundary
    
