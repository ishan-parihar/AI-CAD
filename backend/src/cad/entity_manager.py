"""Entity management for CAD operations"""

from typing import Dict, List, Tuple, Optional, Any, Union
import uuid
from shapely.geometry import Polygon, Point, LineString
from src.utils import get_logger, validate_point, calculate_area, calculate_perimeter
from .dxf_generator import DXFGenerator


class CADEntity:
    """Base class for CAD entities"""
    
    def __init__(self, entity_type: str, layer: str = "0"):
        self.id = str(uuid.uuid4())
        self.type = entity_type
        self.layer = layer
        self.properties = {}
        self.geometry = None
        self.dxf_entity = None
        self.logger = get_logger(__name__)
    
    def set_property(self, key: str, value: Any):
        """Set entity property"""
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get entity property"""
        return self.properties.get(key, default)
    
    def set_geometry(self, geometry: Polygon):
        """Set Shapely geometry"""
        self.geometry = geometry
    
    def get_area(self) -> float:
        """Get entity area"""
        if self.geometry and self.geometry.is_valid:
            return calculate_area(self.geometry)
        return 0.0
    
    def get_perimeter(self) -> float:
        """Get entity perimeter"""
        if self.geometry and self.geometry.is_valid:
            return calculate_perimeter(self.geometry)
        return 0.0
    
    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Get entity bounds (min_x, min_y, max_x, max_y)"""
        if self.geometry and self.geometry.is_valid:
            return self.geometry.bounds
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'layer': self.layer,
            'properties': self.properties,
            'area': self.get_area(),
            'perimeter': self.get_perimeter(),
            'bounds': self.get_bounds()
        }


class Wall(CADEntity):
    """Wall entity"""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float], 
                 thickness: float = 0.2, layer: str = "WALLS"):
        super().__init__("wall", layer)
        
        self.start_point = validate_point(start_point)
        self.end_point = validate_point(end_point)
        self.thickness = thickness
        
        self.set_property("start_point", self.start_point)
        self.set_property("end_point", self.end_point)
        self.set_property("thickness", thickness)
        
        # Create wall geometry
        self._create_geometry()
    
    def _create_geometry(self):
        """Create wall polygon geometry"""
        import math
        
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return
        
        # Perpendicular direction
        perp_x = -dy / length * self.thickness / 2
        perp_y = dx / length * self.thickness / 2
        
        # Wall vertices
        wall_points = [
            (self.start_point[0] + perp_x, self.start_point[1] + perp_y),
            (self.end_point[0] + perp_x, self.end_point[1] + perp_y),
            (self.end_point[0] - perp_x, self.end_point[1] - perp_y),
            (self.start_point[0] - perp_x, self.start_point[1] - perp_y)
        ]
        
        self.set_geometry(Polygon(wall_points))
    
    def get_length(self) -> float:
        """Get wall length"""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        return (dx**2 + dy**2)**0.5
    
    def get_center_line(self) -> LineString:
        """Get wall center line"""
        return LineString([self.start_point, self.end_point])


class Door(CADEntity):
    """Door entity"""
    
    def __init__(self, position: Tuple[float, float], width: float = 0.8, 
                 angle: float = 0, door_type: str = "single", layer: str = "DOORS"):
        super().__init__("door", layer)
        
        self.position = validate_point(position)
        self.width = width
        self.angle = angle
        self.door_type = door_type
        
        self.set_property("position", self.position)
        self.set_property("width", width)
        self.set_property("angle", angle)
        self.set_property("door_type", door_type)
        
        # Create door geometry (simplified as line)
        self._create_geometry()
    
    def _create_geometry(self):
        """Create door geometry (simplified)"""
        import math
        
        # Door opening as line segment
        half_width = self.width / 2
        angle_rad = math.radians(self.angle)
        
        dx = half_width * math.cos(angle_rad)
        dy = half_width * math.sin(angle_rad)
        
        start = (self.position[0] - dx, self.position[1] - dy)
        end = (self.position[0] + dx, self.position[1] + dy)
        
        self.set_geometry(LineString([start, end]))
    
    def get_swing_arc(self) -> Dict[str, Any]:
        """Get door swing arc parameters"""
        return {
            "center": self.position,
            "radius": self.width,
            "start_angle": self.angle,
            "end_angle": self.angle + 90,
            "type": self.door_type
        }


class Window(CADEntity):
    """Window entity"""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float],
                 width: float = 1.2, sill_height: float = 1.0, layer: str = "WINDOWS"):
        super().__init__("window", layer)
        
        self.start_point = validate_point(start_point)
        self.end_point = validate_point(end_point)
        self.width = width
        self.sill_height = sill_height
        
        self.set_property("start_point", self.start_point)
        self.set_property("end_point", self.end_point)
        self.set_property("width", width)
        self.set_property("sill_height", sill_height)
        
        # Create window geometry
        self._create_geometry()
    
    def _create_geometry(self):
        """Create window geometry"""
        self.set_geometry(LineString([self.start_point, self.end_point]))
    
    def get_length(self) -> float:
        """Get window length"""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        return (dx**2 + dy**2)**0.5


class Room(CADEntity):
    """Room entity"""
    
    def __init__(self, polygon_points: List[Tuple[float, float]], 
                 room_type: str = "room", name: str = "", layer: str = "ROOMS"):
        super().__init__("room", layer)
        
        self.room_type = room_type
        self.name = name
        self.polygon_points = [validate_point(p) for p in polygon_points]
        
        self.set_property("room_type", room_type)
        self.set_property("name", name)
        self.set_property("polygon_points", self.polygon_points)
        
        # Create room geometry
        self._create_geometry()
    
    def _create_geometry(self):
        """Create room geometry"""
        if len(self.polygon_points) >= 3:
            self.set_geometry(Polygon(self.polygon_points))
    
    def get_centroid(self) -> Optional[Tuple[float, float]]:
        """Get room centroid"""
        if self.geometry and self.geometry.is_valid:
            centroid = self.geometry.centroid
            return (centroid.x, centroid.y)
        return None
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Check if room contains point"""
        if self.geometry and self.geometry.is_valid:
            return self.geometry.contains(Point(point))
        return False


class Dimension(CADEntity):
    """Dimension entity"""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float],
                 text_point: Tuple[float, float], dimension_type: str = "linear",
                 layer: str = "DIMENSIONS"):
        super().__init__("dimension", layer)
        
        self.start_point = validate_point(start_point)
        self.end_point = validate_point(end_point)
        self.text_point = validate_point(text_point)
        self.dimension_type = dimension_type
        
        self.set_property("start_point", self.start_point)
        self.set_property("end_point", self.end_point)
        self.set_property("text_point", self.text_point)
        self.set_property("dimension_type", dimension_type)
        
        # Calculate measured value
        self._calculate_measurement()
    
    def _calculate_measurement(self):
        """Calculate dimension measurement"""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        
        if self.dimension_type == "linear":
            measurement = (dx**2 + dy**2)**0.5
        elif self.dimension_type == "horizontal":
            measurement = abs(dx)
        elif self.dimension_type == "vertical":
            measurement = abs(dy)
        else:
            measurement = (dx**2 + dy**2)**0.5
        
        self.set_property("measurement", measurement)


class Text(CADEntity):
    """Text entity"""
    
    def __init__(self, text: str, position: Tuple[float, float], 
                 height: float = 0.3, rotation: float = 0, layer: str = "TEXT"):
        super().__init__("text", layer)
        
        self.text = text
        self.position = validate_point(position)
        self.height = height
        self.rotation = rotation
        
        self.set_property("text", text)
        self.set_property("position", self.position)
        self.set_property("height", height)
        self.set_property("rotation", rotation)


class EntityManager:
    """Manages CAD entities and their relationships"""
    
    def __init__(self, dxf_generator: DXFGenerator):
        self.dxf_generator = dxf_generator
        self.entities: Dict[str, CADEntity] = {}
        self.entities_by_type: Dict[str, List[str]] = {}
        self.entities_by_layer: Dict[str, List[str]] = {}
        self.logger = get_logger(__name__)
    
    def add_entity(self, entity: CADEntity) -> str:
        """Add entity to manager"""
        self.entities[entity.id] = entity
        
        # Index by type
        if entity.type not in self.entities_by_type:
            self.entities_by_type[entity.type] = []
        self.entities_by_type[entity.type].append(entity.id)
        
        # Index by layer
        if entity.layer not in self.entities_by_layer:
            self.entities_by_layer[entity.layer] = []
        self.entities_by_layer[entity.layer].append(entity.id)
        
        self.logger.info(f"Added {entity.type} entity: {entity.id}")
        return entity.id
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove entity from manager"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        
        # Remove from type index
        if entity.type in self.entities_by_type:
            self.entities_by_type[entity.type].remove(entity_id)
        
        # Remove from layer index
        if entity.layer in self.entities_by_layer:
            self.entities_by_layer[entity.layer].remove(entity_id)
        
        # Remove entity
        del self.entities[entity_id]
        
        self.logger.info(f"Removed entity: {entity_id}")
        return True
    
    def get_entity(self, entity_id: str) -> Optional[CADEntity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: str) -> List[CADEntity]:
        """Get all entities of specific type"""
        entity_ids = self.entities_by_type.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_entities_by_layer(self, layer: str) -> List[CADEntity]:
        """Get all entities on specific layer"""
        entity_ids = self.entities_by_layer.get(layer, [])
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def find_entities_at_point(self, point: Tuple[float, float], 
                              tolerance: float = 0.1) -> List[CADEntity]:
        """Find entities at or near a point"""
        found_entities = []
        point_obj = Point(point)
        
        for entity in self.entities.values():
            if entity.geometry and entity.geometry.is_valid:
                # Expand point with tolerance
                buffer_zone = point_obj.buffer(tolerance)
                if entity.geometry.intersects(buffer_zone):
                    found_entities.append(entity)
        
        return found_entities
    
    def find_intersecting_entities(self, entity_id: str) -> List[CADEntity]:
        """Find entities that intersect with the given entity"""
        if entity_id not in self.entities:
            return []
        
        target_entity = self.entities[entity_id]
        if not target_entity.geometry or not target_entity.geometry.is_valid:
            return []
        
        intersecting = []
        for eid, entity in self.entities.items():
            if eid == entity_id:
                continue
            
            if entity.geometry and entity.geometry.is_valid:
                if target_entity.geometry.intersects(entity.geometry):
                    intersecting.append(entity)
        
        return intersecting
    
    def get_rooms_adjacent_to_room(self, room_id: str) -> List[Room]:
        """Find rooms adjacent to a given room"""
        if room_id not in self.entities:
            return []
        
        room = self.entities[room_id]
        if room.type != "room" or not room.geometry or not room.geometry.is_valid:
            return []
        
        adjacent_rooms = []
        rooms = self.get_entities_by_type("room")
        
        for other_room in rooms:
            if other_room.id == room_id:
                continue
            
            if other_room.geometry and other_room.geometry.is_valid:
                # Check if rooms are adjacent (touching or very close)
                distance = room.geometry.distance(other_room.geometry)
                if distance < 0.5:  # Within 0.5 meters
                    adjacent_rooms.append(other_room)
        
        return adjacent_rooms
    
    def calculate_total_area(self, entity_type: str = None) -> float:
        """Calculate total area of entities"""
        total_area = 0.0
        
        entities = self.entities.values()
        if entity_type:
            entities = self.get_entities_by_type(entity_type)
        
        for entity in entities:
            total_area += entity.get_area()
        
        return total_area
    
    def calculate_space_utilization(self, boundary_polygon: Polygon) -> float:
        """Calculate space utilization percentage"""
        boundary_area = calculate_area(boundary_polygon)
        if boundary_area == 0:
            return 0.0
        
        room_area = self.calculate_total_area("room")
        return (room_area / boundary_area) * 100
    
    def validate_layout(self) -> Dict[str, Any]:
        """Validate layout for common issues"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check for overlapping rooms
        rooms = self.get_entities_by_type("room")
        for i, room1 in enumerate(rooms):
            for room2 in rooms[i+1:]:
                if (room1.geometry and room1.geometry.is_valid and 
                    room2.geometry and room2.geometry.is_valid):
                    
                    if room1.geometry.intersects(room2.geometry):
                        validation_result["valid"] = False
                        validation_result["issues"].append(
                            f"Rooms overlap: {room1.get_property('name', room1.id)} and "
                            f"{room2.get_property('name', room2.id)}"
                        )
        
        # Check for isolated rooms (no doors)
        for room in rooms:
            room_name = room.get_property('name', room.id)
            room_polygon = room.geometry
            
            # Find doors in or near this room
            doors = self.get_entities_by_type("door")
            has_door = False
            
            for door in doors:
                if door.geometry and door.geometry.is_valid:
                    # Check if door is within room bounds
                    if room_polygon and room_polygon.contains(door.geometry.centroid):
                        has_door = True
                        break
            
            if not has_door:
                validation_result["warnings"].append(f"Room '{room_name}' has no doors")
        
        # Calculate statistics
        validation_result["statistics"] = {
            "total_entities": len(self.entities),
            "rooms": len(rooms),
            "walls": len(self.get_entities_by_type("wall")),
            "doors": len(self.get_entities_by_type("door")),
            "windows": len(self.get_entities_by_type("window")),
            "total_room_area": self.calculate_total_area("room")
        }
        
        return validation_result
    
    def export_to_dxf(self) -> bool:
        """Export all entities to DXF"""
        try:
            for entity in self.entities.values():
                if entity.type == "wall":
                    wall = entity
                    wall.dxf_entity = self.dxf_generator.add_wall(
                        start_point=wall.start_point,
                        end_point=wall.end_point,
                        thickness=wall.thickness,
                        layer=wall.layer
                    )
                
                elif entity.type == "door":
                    door = entity
                    door.dxf_entity = self.dxf_generator.add_door(
                        position=door.position,
                        width=door.width,
                        angle=door.angle,
                        door_type=door.door_type,
                        layer=door.layer
                    )
                
                elif entity.type == "window":
                    window = entity
                    window.dxf_entity = self.dxf_generator.add_window(
                        start_point=window.start_point,
                        end_point=window.end_point,
                        width=window.width,
                        sill_height=window.sill_height,
                        layer=window.layer
                    )
                
                elif entity.type == "room":
                    room = entity
                    room.dxf_entity = self.dxf_generator.add_room(
                        polygon_points=room.polygon_points,
                        room_name=room.name,
                        layer=room.layer
                    )
                
                elif entity.type == "dimension":
                    dimension = entity
                    dimension.dxf_entity = self.dxf_generator.add_dimension(
                        start_point=dimension.start_point,
                        end_point=dimension.end_point,
                        text_point=dimension.text_point,
                        dimension_type=dimension.dimension_type,
                        layer=dimension.layer
                    )
                
                elif entity.type == "text":
                    text = entity
                    text.dxf_entity = self.dxf_generator.add_text(
                        text=text.text,
                        position=text.position,
                        height=text.height,
                        rotation=text.rotation,
                        layer=text.layer
                    )
            
            self.logger.info("Exported all entities to DXF")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export entities to DXF: {e}")
            return False
    
    def get_layout_summary(self) -> Dict[str, Any]:
        """Get layout summary information"""
        rooms = self.get_entities_by_type("room")
        
        summary = {
            "entity_counts": {
                entity_type: len(entities) 
                for entity_type, entities in self.entities_by_type.items()
            },
            "room_summary": {},
            "layer_summary": {
                layer: len(entity_ids)
                for layer, entity_ids in self.entities_by_layer.items()
            },
            "total_area": self.calculate_total_area(),
            "room_details": []
        }
        
        # Room-specific summary
        room_types = {}
        for room in rooms:
            room_type = room.get_property("room_type", "unknown")
            if room_type not in room_types:
                room_types[room_type] = {"count": 0, "total_area": 0}
            
            room_types[room_type]["count"] += 1
            room_types[room_type]["total_area"] += room.get_area()
            
            summary["room_details"].append({
                "id": room.id,
                "name": room.get_property("name", ""),
                "type": room_type,
                "area": room.get_area(),
                "perimeter": room.get_perimeter()
            })
        
        summary["room_summary"] = room_types
        
        return summary