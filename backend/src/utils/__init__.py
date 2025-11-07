"""Utility module initialization"""

from .config import settings
from .logger import get_logger
from .helpers import *

__all__ = [
    'settings',
    'get_logger',
    'validate_point',
    'validate_rectangle',
    'calculate_area',
    'calculate_perimeter',
    'point_in_polygon',
    'polygons_intersect',
    'buffer_polygon',
    'rotate_point',
    'distance_between_points',
    'normalize_angle',
    'degrees_to_radians',
    'radians_to_degrees',
    'create_rectangle_from_center',
    'simplify_polygon',
    'merge_polygons',
    'format_coordinate',
    'is_clockwise'
]