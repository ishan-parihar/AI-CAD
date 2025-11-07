"""Spatial reasoning tools for room placement and layout optimization"""

import math
import networkx as nx
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Point, Polygon, box
from shapely.ops import nearest_points
from .base import Tool, ToolResult
from src.utils import (
    validate_point, calculate_area, distance_between_points,
    create_rectangle_from_center, point_in_polygon, polygons_intersect
)


class SpatialReasoningTool(Tool):
    """Tool for spatial reasoning and room placement optimization"""
    
    def __init__(self):
        super().__init__(
            name="spatial_reasoning",
            description="Performs spatial reasoning for room placement and layout optimization"
        )
        self.min_room_sizes = {
            "bedroom": {"min_area": 7.0, "min_width": 2.4, "min_depth": 3.0},
            "kitchen": {"min_area": 5.0, "min_width": 1.8, "min_depth": 2.4},
            "living_room": {"min_area": 12.0, "min_width": 3.0, "min_depth": 3.6},
            "bathroom": {"min_area": 1.8, "min_width": 1.2, "min_depth": 1.5},
            "dining_room": {"min_area": 8.0, "min_width": 2.4, "min_depth": 2.4},
            "hallway": {"min_width": 0.8, "min_area": 0.0},
            "closet": {"min_area": 0.8, "min_width": 0.6, "min_depth": 0.6},
            "garage": {"min_area": 15.0, "min_width": 3.0, "min_depth": 5.0},
            "office": {"min_area": 7.0, "min_width": 2.4, "min_depth": 2.4},
            "storage": {"min_area": 1.5, "min_width": 1.2, "min_depth": 1.2}
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "place_rooms", "calculate_adjacency", "optimize_circulation",
                        "validate_room_sizes", "find_optimal_layout", "calculate_accessibility"
                    ],
                    "description": "Spatial reasoning operation to perform"
                },
                "boundary": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "Building boundary as polygon vertices"
                },
                "rooms": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "area": {"type": "number"},
                            "preferred_width": {"type": "number"},
                            "preferred_depth": {"type": "number"},
                            "adjacency": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "description": "Room specifications"
                },
                "existing_rooms": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "polygon": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}
                        }
                    }
                },
                "constraints": {
                    "type": "object",
                    "properties": {
                        "min_hallway_width": {"type": "number"},
                        "max_depth": {"type": "number"},
                        "natural_light_preference": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "required": ["operation"]
        }
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute spatial reasoning operation"""
        try:
            operation = parameters["operation"]
            
            if operation == "place_rooms":
                return self._place_rooms(parameters)
            elif operation == "calculate_adjacency":
                return self._calculate_adjacency(parameters)
            elif operation == "optimize_circulation":
                return self._optimize_circulation(parameters)
            elif operation == "validate_room_sizes":
                return self._validate_room_sizes(parameters)
            elif operation == "find_optimal_layout":
                return self._find_optimal_layout(parameters)
            elif operation == "calculate_accessibility":
                return self._calculate_accessibility(parameters)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Spatial reasoning operation failed: {str(e)}"
            )
    
    def _place_rooms(self, params: Dict[str, Any]) -> ToolResult:
        """Place rooms within boundary using spatial optimization"""
        if "boundary" not in params or "rooms" not in params:
            return ToolResult(success=False, error="Boundary and rooms parameters required")
        
        boundary_points = [validate_point(p) for p in params["boundary"]]
        boundary = Polygon(boundary_points)
        rooms_spec = params["rooms"]
        existing_rooms = params.get("existing_rooms", [])
        
        # Create adjacency graph
        adjacency_graph = self._create_adjacency_graph(rooms_spec)
        
        # Generate initial layout
        layout = self._generate_initial_layout(boundary, rooms_spec, adjacency_graph, existing_rooms)
        
        # Optimize layout
        optimized_layout = self._optimize_layout(layout, boundary, adjacency_graph)
        
        return ToolResult(
            success=True,
            data={
                "room_layouts": optimized_layout,
                "adjacency_graph": list(adjacency_graph.edges()),
                "total_utilization": self._calculate_space_utilization(optimized_layout, boundary)
            }
        )
    
    def _calculate_adjacency(self, params: Dict[str, Any]) -> ToolResult:
        """Calculate room adjacency relationships"""
        if "rooms" not in params:
            return ToolResult(success=False, error="Rooms parameter required")
        
        rooms = params["rooms"]
        adjacency_graph = self._create_adjacency_graph(rooms)
        
        # Calculate adjacency matrix
        adjacency_matrix = nx.adjacency_matrix(adjacency_graph).todense().tolist()
        
        return ToolResult(
            success=True,
            data={
                "adjacency_graph": list(adjacency_graph.edges()),
                "adjacency_matrix": adjacency_matrix,
                "centrality_scores": dict(nx.degree_centrality(adjacency_graph))
            }
        )
    
    def _optimize_circulation(self, params: Dict[str, Any]) -> ToolResult:
        """Optimize circulation paths and hallway placement"""
        if "rooms" not in params:
            return ToolResult(success=False, error="Rooms parameter required")
        
        room_layouts = params["rooms"]
        min_hallway_width = params.get("constraints", {}).get("min_hallway_width", 0.8)
        
        # Create circulation graph
        circulation_graph = self._create_circulation_graph(room_layouts)
        
        # Find optimal paths
        optimal_paths = self._find_optimal_paths(circulation_graph, min_hallway_width)
        
        # Calculate circulation efficiency
        efficiency_score = self._calculate_circulation_efficiency(optimal_paths, room_layouts)
        
        return ToolResult(
            success=True,
            data={
                "circulation_paths": optimal_paths,
                "efficiency_score": efficiency_score,
                "hallway_placements": self._suggest_hallway_placements(optimal_paths)
            }
        )
    
    def _validate_room_sizes(self, params: Dict[str, Any]) -> ToolResult:
        """Validate room sizes against building code requirements"""
        if "rooms" not in params:
            return ToolResult(success=False, error="Rooms parameter required")
        
        rooms = params["rooms"]
        validation_results = []
        
        for room in rooms:
            room_type = room.get("type", "unknown")
            area = room.get("area", 0)
            width = room.get("width", 0)
            depth = room.get("depth", 0)
            
            validation = self._validate_single_room(room_type, area, width, depth)
            validation_results.append(validation)
        
        return ToolResult(
            success=True,
            data={"room_validations": validation_results}
        )
    
    def _find_optimal_layout(self, params: Dict[str, Any]) -> ToolResult:
        """Find optimal layout using genetic algorithm"""
        if "boundary" not in params or "rooms" not in params:
            return ToolResult(success=False, error="Boundary and rooms parameters required")
        
        boundary_points = [validate_point(p) for p in params["boundary"]]
        boundary = Polygon(boundary_points)
        rooms_spec = params["rooms"]
        
        # Generate multiple layout candidates
        candidates = self._generate_layout_candidates(boundary, rooms_spec, num_candidates=10)
        
        # Evaluate and rank candidates
        evaluated_candidates = []
        for candidate in candidates:
            score = self._evaluate_layout(candidate, boundary)
            evaluated_candidates.append({"layout": candidate, "score": score})
        
        # Sort by score
        evaluated_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return ToolResult(
            success=True,
            data={
                "best_layout": evaluated_candidates[0]["layout"],
                "alternative_layouts": evaluated_candidates[1:3],
                "evaluation_scores": [c["score"] for c in evaluated_candidates]
            }
        )
    
    def _calculate_accessibility(self, params: Dict[str, Any]) -> ToolResult:
        """Calculate accessibility metrics for layout"""
        if "rooms" not in params:
            return ToolResult(success=False, error="Rooms parameter required")
        
        room_layouts = params["rooms"]
        
        # Calculate accessibility metrics
        accessibility_scores = {}
        
        for room in room_layouts:
            room_type = room.get("type")
            room_polygon = Polygon(room.get("polygon", []))
            
            # Distance from entrance
            entrance_distance = self._calculate_entrance_distance(room_polygon, room_layouts)
            
            # Path width analysis
            path_width = self._analyze_path_widths(room_polygon, room_layouts)
            
            # Overall accessibility score
            score = self._calculate_accessibility_score(entrance_distance, path_width)
            accessibility_scores[room_type] = score
        
        return ToolResult(
            success=True,
            data={"accessibility_scores": accessibility_scores}
        )
    
    # Helper methods
    def _create_adjacency_graph(self, rooms: List[Dict[str, Any]]) -> nx.Graph:
        """Create adjacency graph from room specifications"""
        graph = nx.Graph()
        
        for room in rooms:
            room_type = room.get("type")
            graph.add_node(room_type)
            
            # Add adjacency relationships
            for adjacent_room in room.get("adjacency", []):
                graph.add_edge(room_type, adjacent_room)
        
        return graph
    
    def _generate_initial_layout(
        self, 
        boundary: Polygon, 
        rooms: List[Dict[str, Any]], 
        adjacency_graph: nx.Graph,
        existing_rooms: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate initial room layout"""
        layout = []
        existing_rooms = existing_rooms or []
        
        # Place existing rooms first
        for room in existing_rooms:
            layout.append(room)
        
        # Sort rooms by size (larger rooms first)
        sorted_rooms = sorted(rooms, key=lambda x: x.get("area", 0), reverse=True)
        
        # Place rooms one by one
        for room_spec in sorted_rooms:
            room_layout = self._place_single_room(boundary, room_spec, layout, adjacency_graph)
            if room_layout:
                layout.append(room_layout)
        
        return layout
    
    def _place_single_room(
        self, 
        boundary: Polygon, 
        room_spec: Dict[str, Any], 
        existing_layout: List[Dict[str, Any]], 
        adjacency_graph: nx.Graph
    ) -> Optional[Dict[str, Any]]:
        """Place a single room in the layout"""
        room_type = room_spec.get("type")
        preferred_area = room_spec.get("area", 10.0)
        preferred_width = room_spec.get("preferred_width", math.sqrt(preferred_area))
        preferred_depth = room_spec.get("preferred_depth", preferred_area / preferred_width)
        
        # Find adjacent rooms in existing layout
        adjacent_rooms = [r for r in existing_layout if r.get("type") in adjacency_graph.neighbors(room_type)]
        
        # Generate potential positions
        best_position = None
        best_score = -1
        
        for _ in range(50):  # Try 50 random positions
            # Generate random position within boundary
            min_x, min_y, max_x, max_y = boundary.bounds
            x = np.random.uniform(min_x, max_x)
            y = np.random.uniform(min_y, max_y)
            
            # Create room polygon
            room_polygon = create_rectangle_from_center(
                (x, y), preferred_width, preferred_depth
            )
            
            # Check if room fits within boundary
            if not boundary.contains(Polygon(room_polygon)):
                continue
            
            # Check for overlaps with existing rooms
            room_poly = Polygon(room_polygon)
            overlap = False
            for existing_room in existing_layout:
                existing_poly = Polygon(existing_room.get("polygon", []))
                if polygons_intersect(room_poly, existing_poly):
                    overlap = True
                    break
            
            if overlap:
                continue
            
            # Calculate position score
            score = self._calculate_position_score(
                room_polygon, adjacent_rooms, boundary
            )
            
            if score > best_score:
                best_score = score
                best_position = {
                    "type": room_type,
                    "polygon": room_polygon,
                    "area": calculate_area(room_poly),
                    "center": (x, y),
                    "width": preferred_width,
                    "depth": preferred_depth
                }
        
        return best_position
    
    def _calculate_position_score(
        self, 
        room_polygon: List[Tuple[float, float]], 
        adjacent_rooms: List[Dict[str, Any]], 
        boundary: Polygon
    ) -> float:
        """Calculate score for room position"""
        score = 0.0
        room_poly = Polygon(room_polygon)
        room_center = room_poly.centroid
        
        # Adjacency score
        for adj_room in adjacent_rooms:
            adj_poly = Polygon(adj_room.get("polygon", []))
            if adj_poly.is_valid:
                distance = room_center.distance(adj_poly.centroid)
                score += max(0, 1.0 - distance / 10.0)  # Normalize by 10m
        
        # Boundary proximity score (prefer natural light)
        boundary_distance = room_poly.distance(boundary.boundary)
        score += max(0, 1.0 - boundary_distance / 5.0)  # Normalize by 5m
        
        return score
    
    def _optimize_layout(
        self, 
        layout: List[Dict[str, Any]], 
        boundary: Polygon, 
        adjacency_graph: nx.Graph
    ) -> List[Dict[str, Any]]:
        """Optimize room layout using iterative improvement"""
        optimized_layout = layout.copy()
        
        for iteration in range(100):
            improved = False
            
            for i, room in enumerate(optimized_layout):
                # Try moving room slightly
                current_center = room.get("center", (0, 0))
                current_polygon = room.get("polygon", [])
                
                for dx in [-0.5, 0, 0.5]:
                    for dy in [-0.5, 0, 0.5]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        new_center = (current_center[0] + dx, current_center[1] + dy)
                        new_polygon = [
                            (p[0] + dx, p[1] + dy) for p in current_polygon
                        ]
                        
                        # Check if new position is valid
                        new_poly = Polygon(new_polygon)
                        if not boundary.contains(new_poly):
                            continue
                        
                        # Check for overlaps
                        overlap = False
                        for j, other_room in enumerate(optimized_layout):
                            if i == j:
                                continue
                            other_poly = Polygon(other_room.get("polygon", []))
                            if polygons_intersect(new_poly, other_poly):
                                overlap = True
                                break
                        
                        if not overlap:
                            # Calculate improvement
                            old_score = self._calculate_position_score(
                                current_polygon, 
                                [r for j, r in enumerate(optimized_layout) if i != j],
                                boundary
                            )
                            new_score = self._calculate_position_score(
                                new_polygon,
                                [r for j, r in enumerate(optimized_layout) if i != j],
                                boundary
                            )
                            
                            if new_score > old_score:
                                optimized_layout[i] = {
                                    **room,
                                    "polygon": new_polygon,
                                    "center": new_center
                                }
                                improved = True
                                break
                    
                    if improved:
                        break
                
                if improved:
                    break
            
            if not improved:
                break
        
        return optimized_layout
    
    def _calculate_space_utilization(
        self, layout: List[Dict[str, Any]], boundary: Polygon
    ) -> float:
        """Calculate percentage of boundary area utilized"""
        total_room_area = 0
        boundary_area = calculate_area(boundary)
        
        for room in layout:
            room_polygon = Polygon(room.get("polygon", []))
            if room_polygon.is_valid:
                total_room_area += calculate_area(room_polygon)
        
        return (total_room_area / boundary_area) * 100 if boundary_area > 0 else 0
    
    def _validate_single_room(
        self, room_type: str, area: float, width: float, depth: float
    ) -> Dict[str, Any]:
        """Validate single room against requirements"""
        requirements = self.min_room_sizes.get(room_type, {})
        
        validation = {
            "room_type": room_type,
            "valid": True,
            "issues": []
        }
        
        # Check minimum area
        min_area = requirements.get("min_area", 0)
        if area < min_area:
            validation["valid"] = False
            validation["issues"].append(f"Area {area}m² below minimum {min_area}m²")
        
        # Check minimum dimensions
        min_width = requirements.get("min_width", 0)
        min_depth = requirements.get("min_depth", 0)
        
        if width < min_width:
            validation["valid"] = False
            validation["issues"].append(f"Width {width}m below minimum {min_width}m")
        
        if depth < min_depth:
            validation["valid"] = False
            validation["issues"].append(f"Depth {depth}m below minimum {min_depth}m")
        
        return validation
    
    def _create_circulation_graph(self, rooms: List[Dict[str, Any]]) -> nx.Graph:
        """Create circulation graph from room layouts"""
        graph = nx.Graph()
        
        for room in rooms:
            room_type = room.get("type")
            room_polygon = Polygon(room.get("polygon", []))
            
            if room_polygon.is_valid:
                graph.add_node(room_type, centroid=room_polygon.centroid)
        
        # Add edges based on proximity
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms):
                if i >= j:
                    continue
                
                poly1 = Polygon(room1.get("polygon", []))
                poly2 = Polygon(room2.get("polygon", []))
                
                if poly1.is_valid and poly2.is_valid:
                    distance = poly1.distance(poly2)
                    if distance < 5.0:  # Connect rooms within 5m
                        graph.add_edge(
                            room1.get("type"), 
                            room2.get("type"), 
                            weight=distance
                        )
        
        return graph
    
    def _find_optimal_paths(
        self, circulation_graph: nx.Graph, min_width: float
    ) -> List[Dict[str, Any]]:
        """Find optimal circulation paths"""
        paths = []
        
        # Find all pairs shortest paths
        all_pairs = dict(nx.all_pairs_dijkstra_path_length(circulation_graph))
        
        for source, targets in all_pairs.items():
            for target, distance in targets.items():
                if source != target:
                    paths.append({
                        "from": source,
                        "to": target,
                        "distance": distance,
                        "required_width": min_width
                    })
        
        return paths
    
    def _calculate_circulation_efficiency(
        self, paths: List[Dict[str, Any]], rooms: List[Dict[str, Any]]
    ) -> float:
        """Calculate circulation efficiency score"""
        if not paths:
            return 0.0
        
        total_distance = sum(p["distance"] for p in paths)
        avg_distance = total_distance / len(paths)
        
        # Efficiency inversely proportional to average distance
        efficiency = max(0, 1.0 - avg_distance / 20.0)  # Normalize by 20m
        
        return efficiency
    
    def _suggest_hallway_placements(
        self, paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest hallway placements based on circulation paths"""
        # Group paths by similar routes
        hallway_suggestions = []
        
        # This is a simplified implementation
        # In practice, you'd analyze path geometry to find common routes
        common_paths = {}
        
        for path in paths:
            route_key = f"{path['from']}-{path['to']}"
            if route_key not in common_paths:
                common_paths[route_key] = []
            common_paths[route_key].append(path)
        
        for route_key, route_paths in common_paths.items():
            if len(route_paths) >= 2:  # Multiple paths suggest hallway need
                hallway_suggestions.append({
                    "route": route_key,
                    "width": max(p["required_width"] for p in route_paths),
                    "traffic_count": len(route_paths)
                })
        
        return hallway_suggestions
    
    def _generate_layout_candidates(
        self, boundary: Polygon, rooms: List[Dict[str, Any]], num_candidates: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """Generate multiple layout candidates"""
        candidates = []
        
        adjacency_graph = self._create_adjacency_graph(rooms)
        
        for _ in range(num_candidates):
            candidate = self._generate_initial_layout(boundary, rooms, adjacency_graph)
            candidates.append(candidate)
        
        return candidates
    
    def _evaluate_layout(
        self, layout: List[Dict[str, Any]], boundary: Polygon
    ) -> float:
        """Evaluate layout quality"""
        score = 0.0
        
        # Space utilization score
        utilization = self._calculate_space_utilization(layout, boundary)
        score += utilization * 0.3
        
        # Adjacency satisfaction score
        adjacency_score = self._calculate_adjacency_satisfaction(layout)
        score += adjacency_score * 0.4
        
        # Circulation efficiency score
        circulation_score = self._calculate_circulation_score(layout)
        score += circulation_score * 0.3
        
        return score
    
    def _calculate_adjacency_satisfaction(self, layout: List[Dict[str, Any]]) -> float:
        """Calculate how well adjacency requirements are satisfied"""
        # Simplified implementation
        satisfied_adjacencies = 0
        total_required_adjacencies = 0
        
        for room in layout:
            room_type = room.get("type")
            room_polygon = Polygon(room.get("polygon", []))
            
            if not room_polygon.is_valid:
                continue
            
            # Check adjacency with other rooms
            for other_room in layout:
                if room == other_room:
                    continue
                
                other_polygon = Polygon(other_room.get("polygon", []))
                if other_polygon.is_valid and room_polygon.distance(other_polygon) < 1.0:
                    satisfied_adjacencies += 1
                
                total_required_adjacencies += 1
        
        return satisfied_adjacencies / max(1, total_required_adjacencies)
    
    def _calculate_circulation_score(self, layout: List[Dict[str, Any]]) -> float:
        """Calculate circulation efficiency score"""
        circulation_graph = self._create_circulation_graph(layout)
        
        if circulation_graph.number_of_nodes() < 2:
            return 0.0
        
        # Calculate average shortest path length
        avg_path_length = nx.average_shortest_path_length(circulation_graph)
        
        # Normalize score (lower average path length is better)
        score = max(0, 1.0 - avg_path_length / 15.0)  # Normalize by 15m
        
        return score
    
    def _calculate_entrance_distance(
        self, room_polygon: Polygon, all_rooms: List[Dict[str, Any]]
    ) -> float:
        """Calculate distance from room to entrance"""
        # Assume entrance is at boundary centroid
        all_room_polygons = [Polygon(r.get("polygon", [])) for r in all_rooms]
        valid_polygons = [p for p in all_room_polygons if p.is_valid]
        
        if not valid_polygons:
            return 0.0
        
        # Find boundary (union of all rooms)
        boundary = valid_polygons[0].unary_union if len(valid_polygons) > 1 else valid_polygons[0]
        entrance_point = boundary.centroid
        
        return room_polygon.distance(entrance_point)
    
    def _analyze_path_widths(
        self, room_polygon: Polygon, all_rooms: List[Dict[str, Any]]
    ) -> float:
        """Analyze minimum path width to reach room"""
        # Simplified implementation
        return 0.8  # Default minimum width
    
    def _calculate_accessibility_score(
        self, entrance_distance: float, path_width: float
    ) -> float:
        """Calculate overall accessibility score"""
        distance_score = max(0, 1.0 - entrance_distance / 20.0)  # Normalize by 20m
        width_score = min(1.0, path_width / 0.9)  # Normalize by 0.9m
        
        return (distance_score + width_score) / 2.0