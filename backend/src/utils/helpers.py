"""Utility functions and helpers"""

from typing import List, Tuple, Union, Any
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString


def validate_point(point: Union[Tuple[float, float], List[float]]) -> Tuple[float, float]:
    """Validate and convert point to tuple format"""
    if isinstance(point, (list, tuple)) and len(point) == 2:
        x, y = float(point[0]), float(point[1])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError(f"Invalid point coordinates: {point}")
        return (x, y)
    raise ValueError(f"Point must be a tuple/list of 2 numbers, got {point}")


def validate_rectangle(bounds: List[Tuple[float, float]]) -> Polygon:
    """Validate rectangle bounds and return Shapely polygon"""
    if len(bounds) != 4:
        raise ValueError("Rectangle must have exactly 4 points")
    
    validated_points = [validate_point(p) for p in bounds]
    
    # Check if points form a valid rectangle
    polygon = Polygon(validated_points)
    if not polygon.is_valid:
        raise ValueError("Invalid rectangle geometry")
    
    return polygon


def calculate_area(polygon: Polygon) -> float:
    """Calculate area of a polygon"""
    return polygon.area


def calculate_perimeter(polygon: Polygon) -> float:
    """Calculate perimeter of a polygon"""
    return polygon.length


def point_in_polygon(point: Tuple[float, float], polygon: Polygon) -> bool:
    """Check if point is inside polygon"""
    return polygon.contains(Point(point))


def polygons_intersect(poly1: Polygon, poly2: Polygon) -> bool:
    """Check if two polygons intersect"""
    return poly1.intersects(poly2)


def buffer_polygon(polygon: Polygon, distance: float) -> Polygon:
    """Buffer polygon by given distance"""
    return polygon.buffer(distance)


def rotate_point(point: Tuple[float, float], angle: float, origin: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """Rotate point around origin by given angle (in radians)"""
    x, y = point
    ox, oy = origin
    
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    new_x = ox + (x - ox) * cos_angle - (y - oy) * sin_angle
    new_y = oy + (x - ox) * sin_angle + (y - oy) * cos_angle
    
    return (new_x, new_y)


def distance_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def normalize_angle(angle: float) -> float:
    """Normalize angle to [0, 2π] range"""
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return radians * 180 / math.pi


def create_rectangle_from_center(
    center: Tuple[float, float],
    width: float,
    height: float,
    angle: float = 0
) -> List[Tuple[float, float]]:
    """Create rectangle points from center, dimensions, and rotation angle"""
    cx, cy = center
    half_w, half_h = width / 2, height / 2
    
    # Create rectangle corners relative to center
    corners = [
        (-half_w, -half_h),
        (half_w, -half_h),
        (half_w, half_h),
        (-half_w, half_h)
    ]
    
    # Rotate corners if angle is specified
    if angle != 0:
        corners = [rotate_point(corner, angle) for corner in corners]
    
    # Translate to actual center position
    rectangle = [(cx + x, cy + y) for x, y in corners]
    
    return rectangle


def simplify_polygon(polygon: Polygon, tolerance: float = 0.01) -> Polygon:
    """Simplify polygon by removing redundant vertices"""
    return polygon.simplify(tolerance, preserve_topology=True)


def merge_polygons(polygons: List[Polygon]) -> Polygon:
    """Merge multiple polygons into one"""
    if not polygons:
        raise ValueError("Cannot merge empty list of polygons")
    
    result = polygons[0]
    for poly in polygons[1:]:
        result = result.union(poly)
    
    return result


def format_coordinate(coord: float, precision: int = 3) -> float:
    """Format coordinate to specified precision"""
    return round(coord, precision)


def is_clockwise(points: List[Tuple[float, float]]) -> bool:
    """Check if polygon points are in clockwise order"""
    if len(points) < 3:
        return False
    
    total = 0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        total += (x2 - x1) * (y2 + y1)
    
    return total < 0