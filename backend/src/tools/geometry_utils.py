"""Geometric utilities and calculations"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union, split
from .base import Tool, ToolResult
from src.utils import (
    validate_point, validate_rectangle, calculate_area, 
    calculate_perimeter, distance_between_points, rotate_point,
    create_rectangle_from_center, buffer_polygon, polygons_intersect
)


class GeometryUtilsTool(Tool):
    """Tool for geometric calculations and manipulations"""
    
    def __init__(self):
        super().__init__(
            name="geometry_utils",
            description="Performs geometric calculations and manipulations for floor planning"
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "calculate_area", "calculate_perimeter", "distance",
                        "rotate_point", "create_rectangle", "buffer_polygon",
                        "check_intersection", "split_polygon", "merge_polygons"
                    ],
                    "description": "Geometric operation to perform"
                },
                "points": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "Array of points [[x1, y1], [x2, y2], ...]"
                },
                "polygon": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "Polygon vertices [[x1, y1], [x2, y2], ...]"
                },
                "distance": {"type": "number", "description": "Distance for buffering"},
                "angle": {"type": "number", "description": "Angle in degrees"},
                "center": {"type": "array", "items": {"type": "number"}, "description": "Center point [x, y]"},
                "width": {"type": "number", "description": "Rectangle width"},
                "height": {"type": "number", "description": "Rectangle height"}
            },
            "required": ["operation"]
        }
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute geometric operation"""
        try:
            operation = parameters["operation"]
            
            if operation == "calculate_area":
                return self._calculate_area(parameters)
            elif operation == "calculate_perimeter":
                return self._calculate_perimeter(parameters)
            elif operation == "distance":
                return self._calculate_distance(parameters)
            elif operation == "rotate_point":
                return self._rotate_point(parameters)
            elif operation == "create_rectangle":
                return self._create_rectangle(parameters)
            elif operation == "buffer_polygon":
                return self._buffer_polygon(parameters)
            elif operation == "check_intersection":
                return self._check_intersection(parameters)
            elif operation == "split_polygon":
                return self._split_polygon(parameters)
            elif operation == "merge_polygons":
                return self._merge_polygons(parameters)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Geometry operation failed: {str(e)}"
            )
    
    def _calculate_area(self, params: Dict[str, Any]) -> ToolResult:
        """Calculate area of polygon"""
        if "polygon" not in params:
            return ToolResult(success=False, error="Polygon parameter required")
        
        polygon_points = [validate_point(p) for p in params["polygon"]]
        polygon = Polygon(polygon_points)
        
        return ToolResult(
            success=True,
            data={"area": calculate_area(polygon)}
        )
    
    def _calculate_perimeter(self, params: Dict[str, Any]) -> ToolResult:
        """Calculate perimeter of polygon"""
        if "polygon" not in params:
            return ToolResult(success=False, error="Polygon parameter required")
        
        polygon_points = [validate_point(p) for p in params["polygon"]]
        polygon = Polygon(polygon_points)
        
        return ToolResult(
            success=True,
            data={"perimeter": calculate_perimeter(polygon)}
        )
    
    def _calculate_distance(self, params: Dict[str, Any]) -> ToolResult:
        """Calculate distance between two points"""
        if "points" not in params or len(params["points"]) != 2:
            return ToolResult(success=False, error="Two points required")
        
        p1 = validate_point(params["points"][0])
        p2 = validate_point(params["points"][1])
        
        distance = distance_between_points(p1, p2)
        
        return ToolResult(
            success=True,
            data={"distance": distance}
        )
    
    def _rotate_point(self, params: Dict[str, Any]) -> ToolResult:
        """Rotate point around origin"""
        required = ["point", "angle"]
        if not all(k in params for k in required):
            return ToolResult(success=False, error=f"Required parameters: {required}")
        
        point = validate_point(params["point"])
        angle_deg = params["angle"]
        origin = params.get("origin", [0, 0])
        origin = validate_point(origin)
        
        angle_rad = math.radians(angle_deg)
        rotated = rotate_point(point, angle_rad, origin)
        
        return ToolResult(
            success=True,
            data={"rotated_point": rotated}
        )
    
    def _create_rectangle(self, params: Dict[str, Any]) -> ToolResult:
        """Create rectangle from center and dimensions"""
        required = ["center", "width", "height"]
        if not all(k in params for k in required):
            return ToolResult(success=False, error=f"Required parameters: {required}")
        
        center = validate_point(params["center"])
        width = params["width"]
        height = params["height"]
        angle = params.get("angle", 0)
        
        rectangle = create_rectangle_from_center(center, width, height, math.radians(angle))
        
        return ToolResult(
            success=True,
            data={"rectangle": rectangle}
        )
    
    def _buffer_polygon(self, params: Dict[str, Any]) -> ToolResult:
        """Buffer polygon by distance"""
        required = ["polygon", "distance"]
        if not all(k in params for k in required):
            return ToolResult(success=False, error=f"Required parameters: {required}")
        
        polygon_points = [validate_point(p) for p in params["polygon"]]
        polygon = Polygon(polygon_points)
        distance = params["distance"]
        
        buffered = buffer_polygon(polygon, distance)
        
        return ToolResult(
            success=True,
            data={"buffered_polygon": list(buffered.exterior.coords)}
        )
    
    def _check_intersection(self, params: Dict[str, Any]) -> ToolResult:
        """Check if two polygons intersect"""
        required = ["polygon1", "polygon2"]
        if not all(k in params for k in required):
            return ToolResult(success=False, error=f"Required parameters: {required}")
        
        poly1_points = [validate_point(p) for p in params["polygon1"]]
        poly2_points = [validate_point(p) for p in params["polygon2"]]
        
        poly1 = Polygon(poly1_points)
        poly2 = Polygon(poly2_points)
        
        intersects = polygons_intersect(poly1, poly2)
        
        return ToolResult(
            success=True,
            data={"intersects": intersects}
        )
    
    def _split_polygon(self, params: Dict[str, Any]) -> ToolResult:
        """Split polygon with line"""
        required = ["polygon", "splitting_line"]
        if not all(k in params for k in required):
            return ToolResult(success=False, error=f"Required parameters: {required}")
        
        polygon_points = [validate_point(p) for p in params["polygon"]]
        line_points = [validate_point(p) for p in params["splitting_line"]]
        
        polygon = Polygon(polygon_points)
        line = LineString(line_points)
        
        result = split(polygon, line)
        
        if isinstance(result, MultiPolygon):
            split_polygons = [list(poly.exterior.coords) for poly in result.geoms]
        else:
            split_polygons = [list(result.exterior.coords)]
        
        return ToolResult(
            success=True,
            data={"split_polygons": split_polygons}
        )
    
    def _merge_polygons(self, params: Dict[str, Any]) -> ToolResult:
        """Merge multiple polygons"""
        if "polygons" not in params:
            return ToolResult(success=False, error="Polygons parameter required")
        
        polygons_data = params["polygons"]
        if not isinstance(polygons_data, list) or len(polygons_data) < 2:
            return ToolResult(success=False, error="At least 2 polygons required")
        
        polygons = []
        for poly_points in polygons_data:
            polygon_points = [validate_point(p) for p in poly_points]
            polygons.append(Polygon(polygon_points))
        
        merged = unary_union(polygons)
        
        if isinstance(merged, MultiPolygon):
            result_polygons = [list(poly.exterior.coords) for poly in merged.geoms]
        else:
            result_polygons = [list(merged.exterior.coords)]
        
        return ToolResult(
            success=True,
            data={"merged_polygons": result_polygons}
        )