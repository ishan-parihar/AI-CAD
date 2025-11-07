"""Design rules and validation engine for architectural compliance"""

from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import Polygon, Point, LineString
from .base import Tool, ToolResult
from src.utils import validate_point, calculate_area, calculate_perimeter, point_in_polygon


class DesignRulesTool(Tool):
    """Tool for applying architectural design rules and validation"""
    
    def __init__(self):
        super().__init__(
            name="design_rules",
            description="Applies architectural design rules and validates compliance"
        )
        
        # Building code requirements (simplified)
        self.building_codes = {
            "residential": {
                "min_ceiling_height": 2.4,  # meters
                "min_room_height": 2.1,     # meters
                "max_stair_rise": 0.18,     # meters
                "min_stair_run": 0.28,      # meters
                "min_corridor_width": 0.8,  # meters
                "min_door_width": 0.8,      # meters
                "min_window_area_ratio": 0.08,  # 8% of floor area
                "max_room_depth": 10.0,     # meters for natural light
                "min_kitchen_area": 5.0,    # square meters
                "min_bathroom_area": 1.8,   # square meters
                "min_bedroom_area": 7.0,    # square meters
            }
        }
        
        # Design principles
        self.design_principles = {
            "proportion_rules": {
                "golden_ratio": 1.618,  # Ideal width/height ratio
                "min_aspect_ratio": 0.6,  # Minimum width/height ratio
                "max_aspect_ratio": 2.5   # Maximum width/height ratio
            },
            "circulation_rules": {
                "max_distance_to_entrance": 15.0,  # meters
                "min_circulation_space": 1.2,      # square meters per person
                "max_dead_end_corridor": 7.0       # meters
            },
            "lighting_rules": {
                "max_room_depth_for_light": 6.0,   # meters
                "min_window_width": 0.6,           # meters
                "prefer_south_facing": True
            }
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "validate_room_sizes", "check_egress", "apply_design_principles",
                        "validate_building_codes", "check_natural_lighting", "validate_circulation",
                        "check_accessibility", "apply_feng_shui", "validate_energy_efficiency"
                    ],
                    "description": "Design rule operation to perform"
                },
                "layout": {
                    "type": "object",
                    "properties": {
                        "boundary": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                        "rooms": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "polygon": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                                    "area": {"type": "number"},
                                    "windows": {"type": "array", "items": {"type": "object"}},
                                    "doors": {"type": "array", "items": {"type": "object"}}
                                }
                            }
                        },
                        "building_type": {"type": "string", "enum": ["residential", "commercial", "mixed"]},
                        "stories": {"type": "number"}
                    }
                },
                "requirements": {
                    "type": "object",
                    "properties": {
                        "occupancy": {"type": "number"},
                        "accessibility_needed": {"type": "boolean"},
                        "energy_efficiency_target": {"type": "string"}
                    }
                }
            },
            "required": ["operation"]
        }
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute design rules operation"""
        try:
            operation = parameters["operation"]
            
            if operation == "validate_room_sizes":
                return self._validate_room_sizes(parameters)
            elif operation == "check_egress":
                return self._check_egress(parameters)
            elif operation == "apply_design_principles":
                return self._apply_design_principles(parameters)
            elif operation == "validate_building_codes":
                return self._validate_building_codes(parameters)
            elif operation == "check_natural_lighting":
                return self._check_natural_lighting(parameters)
            elif operation == "validate_circulation":
                return self._validate_circulation(parameters)
            elif operation == "check_accessibility":
                return self._check_accessibility(parameters)
            elif operation == "apply_feng_shui":
                return self._apply_feng_shui(parameters)
            elif operation == "validate_energy_efficiency":
                return self._validate_energy_efficiency(parameters)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Design rules operation failed: {str(e)}"
            )
    
    def _validate_room_sizes(self, params: Dict[str, Any]) -> ToolResult:
        """Validate room sizes against building codes"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        building_type = layout.get("building_type", "residential")
        rooms = layout.get("rooms", [])
        
        codes = self.building_codes.get(building_type, {})
        validation_results = []
        
        for room in rooms:
            room_type = room.get("type", "unknown")
            room_polygon = room.get("polygon", [])
            
            if not room_polygon:
                validation_results.append({
                    "room_type": room_type,
                    "valid": False,
                    "issues": ["Room has no polygon definition"]
                })
                continue
            
            # Calculate actual area
            polygon = Polygon(room_polygon)
            if not polygon.is_valid:
                validation_results.append({
                    "room_type": room_type,
                    "valid": False,
                    "issues": ["Invalid polygon geometry"]
                })
                continue
            
            actual_area = calculate_area(polygon)
            
            # Validate against minimum requirements
            issues = []
            
            # Check specific room type requirements
            if room_type == "kitchen" and actual_area < codes.get("min_kitchen_area", 5.0):
                issues.append(f"Kitchen area {actual_area:.1f}m² below minimum {codes.get('min_kitchen_area')}m²")
            
            elif room_type == "bathroom" and actual_area < codes.get("min_bathroom_area", 1.8):
                issues.append(f"Bathroom area {actual_area:.1f}m² below minimum {codes.get('min_bathroom_area')}m²")
            
            elif room_type == "bedroom" and actual_area < codes.get("min_bedroom_area", 7.0):
                issues.append(f"Bedroom area {actual_area:.1f}m² below minimum {codes.get('min_bedroom_area')}m²")
            
            # Check aspect ratio
            bounds = polygon.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            
            if width > 0 and height > 0:
                aspect_ratio = max(width, height) / min(width, height)
                if aspect_ratio > self.design_principles["proportion_rules"]["max_aspect_ratio"]:
                    issues.append(f"Room aspect ratio {aspect_ratio:.1f} exceeds maximum 2.5")
                elif aspect_ratio < self.design_principles["proportion_rules"]["min_aspect_ratio"]:
                    issues.append(f"Room aspect ratio {aspect_ratio:.1f} below minimum 0.6")
            
            validation_results.append({
                "room_type": room_type,
                "area": actual_area,
                "valid": len(issues) == 0,
                "issues": issues
            })
        
        return ToolResult(
            success=True,
            data={"room_validations": validation_results}
        )
    
    def _check_egress(self, params: Dict[str, Any]) -> ToolResult:
        """Check emergency egress requirements"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        requirements = params.get("requirements", {})
        occupancy = requirements.get("occupancy", 1)
        
        egress_analysis = {
            "total_egress_width": 0,
            "required_egress_width": 0,
            "egress_routes": [],
            "issues": []
        }
        
        # Calculate required egress width (simplified)
        egress_analysis["required_egress_width"] = max(0.8, occupancy * 0.05)  # 5cm per person
        
        # Find exterior doors
        exterior_doors = []
        for room in rooms:
            doors = room.get("doors", [])
            for door in doors:
                if door.get("is_exterior", False):
                    exterior_doors.append(door)
        
        # Calculate total egress width
        for door in exterior_doors:
            door_width = door.get("width", 0.8)
            egress_analysis["total_egress_width"] += door_width
        
        # Validate egress requirements
        if egress_analysis["total_egress_width"] < egress_analysis["required_egress_width"]:
            egress_analysis["issues"].append(
                f"Insufficient egress width: {egress_analysis['total_egress_width']:.1f}m < {egress_analysis['required_egress_width']:.1f}m"
            )
        
        # Check travel distance to exits
        max_travel_distance = 30.0  # meters
        for room in rooms:
            room_polygon = Polygon(room.get("polygon", []))
            if not room_polygon.is_valid:
                continue
            
            room_centroid = room_polygon.centroid
            
            # Find distance to nearest exterior door
            min_distance = float('inf')
            for door in exterior_doors:
                door_position = door.get("position", [0, 0])
                door_point = Point(door_position)
                distance = room_centroid.distance(door_point)
                min_distance = min(min_distance, distance)
            
            if min_distance > max_travel_distance:
                egress_analysis["issues"].append(
                    f"Room {room.get('type')} too far from exit: {min_distance:.1f}m > {max_travel_distance}m"
                )
        
        return ToolResult(
            success=True,
            data=egress_analysis
        )
    
    def _apply_design_principles(self, params: Dict[str, Any]) -> ToolResult:
        """Apply architectural design principles"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        
        analysis = {
            "proportion_score": 0,
            "balance_score": 0,
            "harmony_score": 0,
            "recommendations": []
        }
        
        # Analyze proportions
        proportion_scores = []
        for room in rooms:
            room_polygon = Polygon(room.get("polygon", []))
            if room_polygon.is_valid:
                bounds = room_polygon.bounds
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                
                if width > 0 and height > 0:
                    aspect_ratio = max(width, height) / min(width, height)
                    golden_ratio = self.design_principles["proportion_rules"]["golden_ratio"]
                    
                    # Score based on how close to golden ratio
                    score = 1.0 - abs(aspect_ratio - golden_ratio) / golden_ratio
                    proportion_scores.append(max(0, score))
        
        if proportion_scores:
            analysis["proportion_score"] = sum(proportion_scores) / len(proportion_scores)
        
        # Analyze balance (simplified - check room distribution)
        if rooms:
            boundary_polygon = Polygon(layout.get("boundary", []))
            if boundary_polygon.is_valid:
                boundary_centroid = boundary_polygon.centroid
                
                # Calculate room distribution balance
                room_centroids = []
                for room in rooms:
                    room_polygon = Polygon(room.get("polygon", []))
                    if room_polygon.is_valid:
                        room_centroids.append(room_polygon.centroid)
                
                if room_centroids:
                    # Calculate average distance from boundary centroid
                    avg_distance = sum(
                        centroid.distance(boundary_centroid) for centroid in room_centroids
                    ) / len(room_centroids)
                    
                    # Balance score based on distribution
                    max_possible_distance = boundary_polygon.bounds[2] - boundary_polygon.bounds[0]
                    analysis["balance_score"] = 1.0 - (avg_distance / max_possible_distance)
        
        # Generate recommendations
        if analysis["proportion_score"] < 0.6:
            analysis["recommendations"].append("Consider adjusting room dimensions for better proportions")
        
        if analysis["balance_score"] < 0.5:
            analysis["recommendations"].append("Consider redistributing rooms for better balance")
        
        return ToolResult(
            success=True,
            data=analysis
        )
    
    def _validate_building_codes(self, params: Dict[str, Any]) -> ToolResult:
        """Comprehensive building code validation"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        building_type = layout.get("building_type", "residential")
        
        # Run all relevant validations
        room_size_validation = self._validate_room_sizes(params)
        egress_validation = self._check_egress(params)
        circulation_validation = self._validate_circulation(params)
        
        # Combine results
        combined_validation = {
            "building_type": building_type,
            "overall_compliance": True,
            "validations": {
                "room_sizes": room_size_validation.data if room_size_validation.success else {},
                "egress": egress_validation.data if egress_validation.success else {},
                "circulation": circulation_validation.data if circulation_validation.success else {}
            },
            "critical_issues": [],
            "recommendations": []
        }
        
        # Check for critical issues
        for validation_name, validation_data in combined_validation["validations"].items():
            if isinstance(validation_data, dict):
                if "room_validations" in validation_data:
                    for room_val in validation_data["room_validations"]:
                        if not room_val.get("valid", True):
                            combined_validation["critical_issues"].extend(
                                room_val.get("issues", [])
                            )
                
                if "issues" in validation_data:
                    combined_validation["critical_issues"].extend(validation_data["issues"])
        
        combined_validation["overall_compliance"] = len(combined_validation["critical_issues"]) == 0
        
        return ToolResult(
            success=True,
            data=combined_validation
        )
    
    def _check_natural_lighting(self, params: Dict[str, Any]) -> ToolResult:
        """Check natural lighting requirements"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        
        lighting_analysis = {
            "rooms_with_adequate_light": 0,
            "total_rooms": len(rooms),
            "lighting_issues": []
        }
        
        for room in rooms:
            room_type = room.get("type")
            room_polygon = Polygon(room.get("polygon", []))
            windows = room.get("windows", [])
            
            if not room_polygon.is_valid:
                continue
            
            room_area = calculate_area(room_polygon)
            total_window_area = sum(
                window.get("width", 0) * window.get("height", 0) 
                for window in windows
            )
            
            # Check minimum window area ratio (8% of floor area)
            min_window_area = room_area * 0.08
            
            if total_window_area < min_window_area:
                lighting_analysis["lighting_issues"].append(
                    f"{room_type}: Insufficient window area {total_window_area:.1f}m² < {min_window_area:.1f}m²"
                )
            else:
                lighting_analysis["rooms_with_adequate_light"] += 1
            
            # Check room depth for natural light penetration
            if windows:
                bounds = room_polygon.bounds
                room_depth = bounds[3] - bounds[1]  # North-south depth
                
                if room_depth > self.design_principles["lighting_rules"]["max_room_depth_for_light"]:
                    lighting_analysis["lighting_issues"].append(
                        f"{room_type}: Room depth {room_depth:.1f}m may limit natural light"
                    )
        
        return ToolResult(
            success=True,
            data=lighting_analysis
        )
    
    def _validate_circulation(self, params: Dict[str, Any]) -> ToolResult:
        """Validate circulation and flow"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        
        circulation_analysis = {
            "circulation_efficiency": 0,
            "dead_end_spaces": [],
            "narrow_corridors": [],
            "issues": []
        }
        
        # Find corridors and circulation spaces
        corridors = [room for room in rooms if room.get("type") == "corridor" or room.get("type") == "hallway"]
        
        for corridor in corridors:
            corridor_polygon = Polygon(corridor.get("polygon", []))
            if not corridor_polygon.is_valid:
                continue
            
            # Check minimum corridor width
            bounds = corridor_polygon.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            min_width = min(width, height)
            
            if min_width < self.design_principles["circulation_rules"]["min_corridor_width"]:
                circulation_analysis["narrow_corridors"].append({
                    "corridor_id": corridor.get("id", "unknown"),
                    "width": min_width,
                    "required": self.design_principles["circulation_rules"]["min_corridor_width"]
                })
            
            # Check for dead ends (simplified)
            corridor_length = max(width, height)
            if corridor_length > self.design_principles["circulation_rules"]["max_dead_end_corridor"]:
                circulation_analysis["dead_end_spaces"].append({
                    "corridor_id": corridor.get("id", "unknown"),
                    "length": corridor_length
                })
        
        # Calculate circulation efficiency (simplified)
        total_rooms = len(rooms)
        if total_rooms > 0:
            # Efficiency based on ratio of circulation space to total space
            circulation_area = sum(
                calculate_area(Polygon(corridor.get("polygon", [])))
                for corridor in corridors
                if Polygon(corridor.get("polygon", [])).is_valid
            )
            
            total_area = sum(
                calculate_area(Polygon(room.get("polygon", [])))
                for room in rooms
                if Polygon(room.get("polygon", [])).is_valid
            )
            
            if total_area > 0:
                circulation_ratio = circulation_area / total_area
                # Optimal circulation ratio is around 15-20%
                optimal_ratio = 0.175
                efficiency = 1.0 - abs(circulation_ratio - optimal_ratio) / optimal_ratio
                circulation_analysis["circulation_efficiency"] = max(0, efficiency)
        
        # Generate issues
        for corridor in circulation_analysis["narrow_corridors"]:
            circulation_analysis["issues"].append(
                f"Corridor {corridor['corridor_id']} too narrow: {corridor['width']:.1f}m < {corridor['required']}m"
            )
        
        for dead_end in circulation_analysis["dead_end_spaces"]:
            circulation_analysis["issues"].append(
                f"Corridor {dead_end['corridor_id']} too long: {dead_end['length']:.1f}m > {self.design_principles['circulation_rules']['max_dead_end_corridor']}m"
            )
        
        return ToolResult(
            success=True,
            data=circulation_analysis
        )
    
    def _check_accessibility(self, params: Dict[str, Any]) -> ToolResult:
        """Check accessibility compliance"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        requirements = params.get("requirements", {})
        accessibility_needed = requirements.get("accessibility_needed", False)
        
        if not accessibility_needed:
            return ToolResult(
                success=True,
                data={"accessibility_required": False, "compliance": True}
            )
        
        rooms = layout.get("rooms", [])
        accessibility_analysis = {
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check door widths
        min_door_width = 0.9  # meters for accessibility
        for room in rooms:
            doors = room.get("doors", [])
            for door in doors:
                door_width = door.get("width", 0.8)
                if door_width < min_door_width:
                    accessibility_analysis["issues"].append(
                        f"Door width {door_width:.1f}m below accessibility requirement {min_door_width}m"
                    )
                    accessibility_analysis["compliant"] = False
        
        # Check corridor widths
        min_corridor_width = 1.2  # meters for accessibility
        for room in rooms:
            if room.get("type") in ["corridor", "hallway"]:
                room_polygon = Polygon(room.get("polygon", []))
                if room_polygon.is_valid:
                    bounds = room_polygon.bounds
                    width = bounds[2] - bounds[0]
                    height = bounds[3] - bounds[1]
                    min_dimension = min(width, height)
                    
                    if min_dimension < min_corridor_width:
                        accessibility_analysis["issues"].append(
                            f"Corridor width {min_dimension:.1f}m below accessibility requirement {min_corridor_width}m"
                        )
                        accessibility_analysis["compliant"] = False
        
        # Check for ramps (simplified)
        accessibility_analysis["recommendations"].append("Consider adding ramps for level changes")
        accessibility_analysis["recommendations"].append("Ensure accessible routes to all rooms")
        
        return ToolResult(
            success=True,
            data=accessibility_analysis
        )
    
    def _apply_feng_shui(self, params: Dict[str, Any]) -> ToolResult:
        """Apply Feng Shui principles (simplified)"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        
        feng_shui_analysis = {
            "harmony_score": 0,
            "energy_flow_score": 0,
            "balance_score": 0,
            "recommendations": []
        }
        
        # Simplified Feng Shui analysis
        # Check room arrangement and flow
        
        # Energy flow (avoid direct alignment of doors)
        door_alignments = 0
        total_door_pairs = 0
        
        for room in rooms:
            doors = room.get("doors", [])
            if len(doors) > 1:
                total_door_pairs += len(doors) * (len(doors) - 1) // 2
                # Check if doors are directly aligned (simplified)
                for i, door1 in enumerate(doors):
                    for door2 in doors[i+1:]:
                        pos1 = door1.get("position", [0, 0])
                        pos2 = door2.get("position", [0, 0])
                        
                        # Check if doors are on same wall
                        if abs(pos1[0] - pos2[0]) < 0.5 or abs(pos1[1] - pos2[1]) < 0.5:
                            door_alignments += 1
        
        if total_door_pairs > 0:
            feng_shui_analysis["energy_flow_score"] = 1.0 - (door_alignments / total_door_pairs)
        
        # Balance (symmetry and proportion)
        balance_issues = 0
        for room in rooms:
            room_polygon = Polygon(room.get("polygon", []))
            if room_polygon.is_valid:
                bounds = room_polygon.bounds
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                
                aspect_ratio = max(width, height) / min(width, height)
                if aspect_ratio > 3.0:  # Too elongated
                    balance_issues += 1
        
        if rooms:
            feng_shui_analysis["balance_score"] = 1.0 - (balance_issues / len(rooms))
        
        # Overall harmony score
        feng_shui_analysis["harmony_score"] = (
            feng_shui_analysis["energy_flow_score"] * 0.4 +
            feng_shui_analysis["balance_score"] * 0.6
        )
        
        # Generate recommendations
        if feng_shui_analysis["energy_flow_score"] < 0.6:
            feng_shui_analysis["recommendations"].append("Avoid direct door alignment to improve energy flow")
        
        if feng_shui_analysis["balance_score"] < 0.6:
            feng_shui_analysis["recommendations"].append("Consider more balanced room proportions")
        
        return ToolResult(
            success=True,
            data=feng_shui_analysis
        )
    
    def _validate_energy_efficiency(self, params: Dict[str, Any]) -> ToolResult:
        """Validate energy efficiency considerations"""
        if "layout" not in params:
            return ToolResult(success=False, error="Layout parameter required")
        
        layout = params["layout"]
        rooms = layout.get("rooms", [])
        requirements = params.get("requirements", {})
        energy_target = requirements.get("energy_efficiency_target", "standard")
        
        energy_analysis = {
            "efficiency_score": 0,
            "insulation_potential": 0,
            "natural_lighting_score": 0,
            "recommendations": []
        }
        
        # Calculate building perimeter for heat loss
        boundary_polygon = Polygon(layout.get("boundary", []))
        if boundary_polygon.is_valid:
            perimeter = calculate_perimeter(boundary_polygon)
            area = calculate_area(boundary_polygon)
            
            # Perimeter-to-area ratio (lower is better for energy efficiency)
            if area > 0:
                perimeter_area_ratio = perimeter / area
                energy_analysis["insulation_potential"] = max(0, 1.0 - perimeter_area_ratio / 10.0)
        
        # Analyze window placement for natural lighting and solar gain
        total_window_area = 0
        south_facing_windows = 0
        
        for room in rooms:
            windows = room.get("windows", [])
            for window in windows:
                window_area = window.get("width", 0) * window.get("height", 0)
                total_window_area += window_area
                
                # Check orientation (simplified)
                if window.get("orientation", "") == "south":
                    south_facing_windows += window_area
        
        # Natural lighting score
        if boundary_polygon.is_valid:
            building_area = calculate_area(boundary_polygon)
            if building_area > 0:
                window_area_ratio = total_window_area / building_area
                # Optimal window area ratio is around 15-20%
                optimal_ratio = 0.175
                energy_analysis["natural_lighting_score"] = 1.0 - abs(window_area_ratio - optimal_ratio) / optimal_ratio
        
        # Overall efficiency score
        energy_analysis["efficiency_score"] = (
            energy_analysis["insulation_potential"] * 0.4 +
            energy_analysis["natural_lighting_score"] * 0.6
        )
        
        # Generate recommendations
        if energy_analysis["insulation_potential"] < 0.5:
            energy_analysis["recommendations"].append("Consider more compact design to reduce heat loss")
        
        if energy_analysis["natural_lighting_score"] < 0.6:
            energy_analysis["recommendations"].append("Optimize window placement for better natural lighting")
        
        if south_facing_windows < total_window_area * 0.3:
            energy_analysis["recommendations"].append("Consider more south-facing windows for passive solar heating")
        
        return ToolResult(
            success=True,
            data=energy_analysis
        )