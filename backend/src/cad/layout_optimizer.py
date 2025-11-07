"""Layout optimization algorithms for floor plans"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union, nearest_points
from src.utils import get_logger, calculate_area, distance_between_points
from .entity_manager import EntityManager, Room, Wall, Door, Window


class LayoutOptimizer:
    """Optimizes floor plan layouts using various algorithms"""
    
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.logger = get_logger(__name__)
        
        # Optimization weights
        self.weights = {
            "space_efficiency": 0.3,
            "adjacency_satisfaction": 0.25,
            "circulation_efficiency": 0.2,
            "natural_lighting": 0.15,
            "proportion_quality": 0.1
        }
    
    def optimize_layout(
        self, 
        boundary_polygon: Polygon,
        adjacency_requirements: Dict[str, List[str]] = None,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """Main layout optimization function"""
        try:
            self.logger.info("Starting layout optimization")
            
            # Get current rooms
            rooms = self.entity_manager.get_entities_by_type("room")
            if not rooms:
                return {"success": False, "error": "No rooms found to optimize"}
            
            # Calculate initial score
            initial_score = self._evaluate_layout_quality(rooms, boundary_polygon, adjacency_requirements)
            self.logger.info(f"Initial layout score: {initial_score:.3f}")
            
            # Run optimization iterations
            best_rooms = rooms.copy()
            best_score = initial_score
            
            for iteration in range(max_iterations):
                # Generate perturbation
                perturbed_rooms = self._perturb_layout(rooms, boundary_polygon)
                
                # Evaluate perturbed layout
                perturbed_score = self._evaluate_layout_quality(
                    perturbed_rooms, boundary_polygon, adjacency_requirements
                )
                
                # Accept if better
                if perturbed_score > best_score:
                    best_score = perturbed_score
                    best_rooms = perturbed_rooms
                    self.logger.info(f"Iteration {iteration}: New best score: {best_score:.3f}")
            
            # Apply optimized layout
            self._apply_optimized_layout(best_rooms)
            
            final_score = self._evaluate_layout_quality(best_rooms, boundary_polygon, adjacency_requirements)
            
            self.logger.info(f"Layout optimization completed. Final score: {final_score:.3f}")
            
            return {
                "success": True,
                "initial_score": initial_score,
                "final_score": final_score,
                "improvement": final_score - initial_score,
                "iterations": max_iterations
            }
            
        except Exception as e:
            self.logger.error(f"Layout optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _evaluate_layout_quality(
        self, 
        rooms: List[Room], 
        boundary_polygon: Polygon,
        adjacency_requirements: Dict[str, List[str]] = None
    ) -> float:
        """Evaluate overall layout quality"""
        scores = {}
        
        # Space efficiency
        scores["space_efficiency"] = self._calculate_space_efficiency(rooms, boundary_polygon)
        
        # Adjacency satisfaction
        scores["adjacency_satisfaction"] = self._calculate_adjacency_satisfaction(
            rooms, adjacency_requirements or {}
        )
        
        # Circulation efficiency
        scores["circulation_efficiency"] = self._calculate_circulation_efficiency(rooms)
        
        # Natural lighting
        scores["natural_lighting"] = self._calculate_natural_lighting_score(rooms, boundary_polygon)
        
        # Proportion quality
        scores["proportion_quality"] = self._calculate_proportion_quality(rooms)
        
        # Weighted total score
        total_score = sum(
            scores[metric] * self.weights[metric] 
            for metric in scores
        )
        
        return total_score
    
    def _calculate_space_efficiency(self, rooms: List[Room], boundary_polygon: Polygon) -> float:
        """Calculate space utilization efficiency"""
        if not boundary_polygon.is_valid:
            return 0.0
        
        boundary_area = calculate_area(boundary_polygon)
        if boundary_area == 0:
            return 0.0
        
        total_room_area = sum(room.get_area() for room in rooms if room.geometry and room.geometry.is_valid)
        
        # Ideal utilization is around 80-85% (leave space for circulation, etc.)
        utilization_ratio = total_room_area / boundary_area
        ideal_ratio = 0.825
        
        # Score based on how close to ideal ratio
        score = 1.0 - abs(utilization_ratio - ideal_ratio) / ideal_ratio
        return max(0, score)
    
    def _calculate_adjacency_satisfaction(
        self, 
        rooms: List[Room], 
        adjacency_requirements: Dict[str, List[str]]
    ) -> float:
        """Calculate how well adjacency requirements are satisfied"""
        if not adjacency_requirements:
            return 1.0  # No requirements, perfect score
        
        total_requirements = 0
        satisfied_requirements = 0
        
        # Create room lookup by type
        rooms_by_type = {}
        for room in rooms:
            room_type = room.get_property("room_type", "unknown")
            if room_type not in rooms_by_type:
                rooms_by_type[room_type] = []
            rooms_by_type[room_type].append(room)
        
        # Check adjacency requirements
        for room_type, required_adjacents in adjacency_requirements.items():
            if room_type not in rooms_by_type:
                continue
            
            for room in rooms_by_type[room_type]:
                if not room.geometry or not room.geometry.is_valid:
                    continue
                
                for required_type in required_adjacents:
                    if required_type not in rooms_by_type:
                        continue
                    
                    total_requirements += 1
                    
                    # Check if room has adjacency to required type
                    has_adjacency = False
                    for adjacent_room in rooms_by_type[required_type]:
                        if not adjacent_room.geometry or not adjacent_room.geometry.is_valid:
                            continue
                        
                        # Check if rooms are adjacent (touching or close)
                        distance = room.geometry.distance(adjacent_room.geometry)
                        if distance < 1.0:  # Within 1 meter
                            has_adjacency = True
                            break
                    
                    if has_adjacency:
                        satisfied_requirements += 1
        
        if total_requirements == 0:
            return 1.0
        
        return satisfied_requirements / total_requirements
    
    def _calculate_circulation_efficiency(self, rooms: List[Room]) -> float:
        """Calculate circulation efficiency"""
        if len(rooms) < 2:
            return 1.0
        
        # Create adjacency graph based on room proximity
        graph = nx.Graph()
        
        for room in rooms:
            if not room.geometry or not room.geometry.is_valid:
                continue
            
            room_type = room.get_property("room_type", room.id)
            graph.add_node(room_type, centroid=room.geometry.centroid)
        
        # Add edges based on proximity
        for i, room1 in enumerate(rooms):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                if (room1.geometry and room1.geometry.is_valid and 
                    room2.geometry and room2.geometry.is_valid):
                    
                    distance = room1.geometry.distance(room2.geometry)
                    if distance < 5.0:  # Within 5 meters
                        type1 = room1.get_property("room_type", room1.id)
                        type2 = room2.get_property("room_type", room2.id)
                        graph.add_edge(type1, type2, weight=distance)
        
        if graph.number_of_nodes() < 2:
            return 1.0
        
        # Calculate average shortest path length
        try:
            avg_path_length = nx.average_shortest_path_length(graph)
            # Lower average path length is better (more efficient circulation)
            score = max(0, 1.0 - avg_path_length / 15.0)  # Normalize by 15m
            return score
        except:
            return 0.5  # Graph is not connected
    
    def _calculate_natural_lighting_score(self, rooms: List[Room], boundary_polygon: Polygon) -> float:
        """Calculate natural lighting potential"""
        if len(rooms) == 0:
            return 0.0
        
        total_lighting_score = 0
        
        for room in rooms:
            if not room.geometry or not room.geometry.is_valid:
                continue
            
            # Check distance to boundary (external walls)
            room_centroid = room.geometry.centroid
            distance_to_boundary = room_centroid.distance(boundary_polygon.boundary)
            
            # Rooms closer to boundary get better natural light
            light_score = max(0, 1.0 - distance_to_boundary / 10.0)  # Normalize by 10m
            total_lighting_score += light_score
        
        return total_lighting_score / len(rooms)
    
    def _calculate_proportion_quality(self, rooms: List[Room]) -> float:
        """Calculate room proportion quality"""
        if len(rooms) == 0:
            return 0.0
        
        total_proportion_score = 0
        
        for room in rooms:
            if not room.geometry or not room.geometry.is_valid:
                continue
            
            bounds = room.geometry.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            
            if width <= 0 or height <= 0:
                continue
            
            aspect_ratio = max(width, height) / min(width, height)
            
            # Ideal aspect ratio is around golden ratio (1.618) or square (1.0)
            golden_ratio = 1.618
            score1 = 1.0 - abs(aspect_ratio - golden_ratio) / golden_ratio
            score2 = 1.0 - abs(aspect_ratio - 1.0)
            
            # Take the better of the two scores
            proportion_score = max(score1, score2)
            total_proportion_score += max(0, proportion_score)
        
        return total_proportion_score / len(rooms)
    
    def _perturb_layout(self, rooms: List[Room], boundary_polygon: Polygon) -> List[Room]:
        """Create perturbed version of layout"""
        perturbed_rooms = []
        
        for room in rooms:
            if not room.geometry or not room.geometry.is_valid:
                perturbed_rooms.append(room)
                continue
            
            # Random perturbation
            if np.random.random() < 0.3:  # 30% chance to perturb each room
                # Random translation
                max_translation = 0.5  # meters
                dx = np.random.uniform(-max_translation, max_translation)
                dy = np.random.uniform(-max_translation, max_translation)
                
                # Translate room polygon
                new_points = [
                    (p[0] + dx, p[1] + dy) 
                    for p in room.polygon_points
                ]
                
                # Check if still within boundary
                new_polygon = Polygon(new_points)
                if new_polygon.is_valid and boundary_polygon.contains(new_polygon):
                    # Create new room with perturbed geometry
                    new_room = Room(
                        polygon_points=new_points,
                        room_type=room.get_property("room_type", "room"),
                        name=room.get_property("name", ""),
                        layer=room.layer
                    )
                    perturbed_rooms.append(new_room)
                else:
                    perturbed_rooms.append(room)
            else:
                perturbed_rooms.append(room)
        
        return perturbed_rooms
    
    def _apply_optimized_layout(self, optimized_rooms: List[Room]) -> None:
        """Apply optimized layout to entity manager"""
        # Remove existing rooms
        existing_rooms = self.entity_manager.get_entities_by_type("room")
        for room in existing_rooms:
            self.entity_manager.remove_entity(room.id)
        
        # Add optimized rooms
        for room in optimized_rooms:
            self.entity_manager.add_entity(room)
    
    def optimize_circulation_paths(self, min_hallway_width: float = 0.8) -> Dict[str, Any]:
        """Optimize circulation paths and hallway placement"""
        try:
            rooms = self.entity_manager.get_entities_by_type("room")
            if len(rooms) < 2:
                return {"success": False, "error": "Need at least 2 rooms"}
            
            # Find circulation bottlenecks
            circulation_analysis = self._analyze_circulation_bottlenecks(rooms)
            
            # Suggest hallway improvements
            hallway_suggestions = self._suggest_hallway_improvements(
                circulation_analysis, min_hallway_width
            )
            
            return {
                "success": True,
                "bottlenecks": circulation_analysis["bottlenecks"],
                "suggestions": hallway_suggestions,
                "efficiency_score": circulation_analysis["efficiency_score"]
            }
            
        except Exception as e:
            self.logger.error(f"Circulation optimization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_circulation_bottlenecks(self, rooms: List[Room]) -> Dict[str, Any]:
        """Analyze circulation bottlenecks"""
        bottlenecks = []
        
        # Find rooms with poor access
        for room in rooms:
            if not room.geometry or not room.geometry.is_valid:
                continue
            
            room_centroid = room.geometry.centroid
            
            # Calculate distance to other rooms
            distances = []
            for other_room in rooms:
                if other_room.id == room.id:
                    continue
                
                if other_room.geometry and other_room.geometry.is_valid:
                    distance = room_centroid.distance(other_room.geometry.centroid)
                    distances.append(distance)
            
            if distances:
                avg_distance = sum(distances) / len(distances)
                if avg_distance > 8.0:  # More than 8m average distance
                    bottlenecks.append({
                        "type": "poor_access",
                        "room_id": room.id,
                        "room_name": room.get_property("name", ""),
                        "avg_distance": avg_distance
                    })
        
        # Check for narrow passages between rooms
        for i, room1 in enumerate(rooms):
            for room2 in rooms[i+1:]:
                if (room1.geometry and room1.geometry.is_valid and 
                    room2.geometry and room2.geometry.is_valid):
                    
                    distance = room1.geometry.distance(room2.geometry)
                    if 0 < distance < 1.0:  # Very narrow passage
                        bottlenecks.append({
                            "type": "narrow_passage",
                            "room1_id": room1.id,
                            "room2_id": room2.id,
                            "distance": distance
                        })
        
        efficiency_score = max(0, 1.0 - len(bottlenecks) / max(1, len(rooms)))
        
        return {
            "bottlenecks": bottlenecks,
            "efficiency_score": efficiency_score
        }
    
    def _suggest_hallway_improvements(
        self, 
        circulation_analysis: Dict[str, Any], 
        min_width: float
    ) -> List[Dict[str, Any]]:
        """Suggest hallway improvements"""
        suggestions = []
        
        for bottleneck in circulation_analysis["bottlenecks"]:
            if bottleneck["type"] == "poor_access":
                suggestions.append({
                    "type": "add_hallway",
                    "room_id": bottleneck["room_id"],
                    "description": f"Add hallway to improve access to {bottleneck['room_name']}",
                    "suggested_width": min_width,
                    "priority": "high"
                })
            
            elif bottleneck["type"] == "narrow_passage":
                suggestions.append({
                    "type": "widen_passage",
                    "room1_id": bottleneck["room1_id"],
                    "room2_id": bottleneck["room2_id"],
                    "description": f"Widen passage between rooms (current: {bottleneck['distance']:.1f}m)",
                    "suggested_width": min_width,
                    "priority": "medium"
                })
        
        return suggestions
    
    def auto_place_doors_windows(
        self, 
        boundary_polygon: Polygon,
        door_placement_strategy: str = "external",
        window_placement_strategy: str = "south_facing"
    ) -> Dict[str, Any]:
        """Automatically place doors and windows"""
        try:
            rooms = self.entity_manager.get_entities_by_type("room")
            placements = {"doors": [], "windows": []}
            
            for room in rooms:
                if not room.geometry or not room.geometry.is_valid:
                    continue
                
                # Place doors
                if door_placement_strategy == "external":
                    door_placements = self._place_external_doors(room, boundary_polygon)
                    placements["doors"].extend(door_placements)
                
                # Place windows
                if window_placement_strategy == "south_facing":
                    window_placements = self._place_south_windows(room, boundary_polygon)
                    placements["windows"].extend(window_placements)
            
            # Apply placements
            self._apply_door_window_placements(placements)
            
            return {
                "success": True,
                "doors_placed": len(placements["doors"]),
                "windows_placed": len(placements["windows"]),
                "placements": placements
            }
            
        except Exception as e:
            self.logger.error(f"Auto placement failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _place_external_doors(self, room: Room, boundary_polygon: Polygon) -> List[Dict[str, Any]]:
        """Place external doors for a room"""
        placements = []
        
        # Find walls on boundary
        room_coords = list(room.geometry.exterior.coords)
        
        for i in range(len(room_coords) - 1):
            wall_start = room_coords[i]
            wall_end = room_coords[i + 1]
            
            # Check if wall is on boundary
            wall_midpoint = Point(
                (wall_start[0] + wall_end[0]) / 2,
                (wall_start[1] + wall_end[1]) / 2
            )
            
            if wall_midpoint.distance(boundary_polygon.boundary) < 0.5:
                # Place door on this wall
                door_position = (
                    (wall_start[0] + wall_end[0]) / 2,
                    (wall_start[1] + wall_end[1]) / 2
                )
                
                # Calculate wall angle
                dx = wall_end[0] - wall_start[0]
                dy = wall_end[1] - wall_start[1]
                angle = np.degrees(np.arctan2(dy, dx))
                
                placements.append({
                    "position": door_position,
                    "angle": angle,
                    "width": 0.8,
                    "room_id": room.id
                })
                break  # One external door per room
        
        return placements
    
    def _place_south_windows(self, room: Room, boundary_polygon: Polygon) -> List[Dict[str, Any]]:
        """Place south-facing windows for a room"""
        placements = []
        
        # Find south-facing walls (simplified: walls with negative Y direction)
        room_coords = list(room.geometry.exterior.coords)
        
        for i in range(len(room_coords) - 1):
            wall_start = room_coords[i]
            wall_end = room_coords[i + 1]
            
            # Check if wall is roughly south-facing
            dx = wall_end[0] - wall_start[0]
            dy = wall_end[1] - wall_start[1]
            
            # South-facing walls have negative Y component
            if dy < -0.1:  # Threshold for "south-facing"
                # Check if wall is on boundary
                wall_midpoint = Point(
                    (wall_start[0] + wall_end[0]) / 2,
                    (wall_start[1] + wall_end[1]) / 2
                )
                
                if wall_midpoint.distance(boundary_polygon.boundary) < 0.5:
                    # Place window on this wall
                    window_start = wall_start
                    window_end = wall_end
                    
                    placements.append({
                        "start_point": window_start,
                        "end_point": window_end,
                        "width": abs(dx),
                        "room_id": room.id
                    })
        
        return placements
    
    def _apply_door_window_placements(self, placements: Dict[str, Any]) -> None:
        """Apply door and window placements"""
        # Remove existing doors and windows
        existing_doors = self.entity_manager.get_entities_by_type("door")
        existing_windows = self.entity_manager.get_entities_by_type("window")
        
        for door in existing_doors:
            self.entity_manager.remove_entity(door.id)
        
        for window in existing_windows:
            self.entity_manager.remove_entity(window.id)
        
        # Add new doors
        for door_data in placements["doors"]:
            door = Door(
                position=door_data["position"],
                width=door_data["width"],
                angle=door_data["angle"],
                layer="DOORS"
            )
            self.entity_manager.add_entity(door)
        
        # Add new windows
        for window_data in placements["windows"]:
            window = Window(
                start_point=window_data["start_point"],
                end_point=window_data["end_point"],
                width=window_data["width"],
                layer="WINDOWS"
            )
            self.entity_manager.add_entity(window)