"""DXF file generation and management using ezdxf"""

import ezdxf
from ezdxf import entities
from typing import Dict, List, Tuple, Optional, Any, Union
import os
from datetime import datetime
from src.utils import get_logger, validate_point, format_coordinate
from src.tools.base import Tool, ToolResult


class DXFGenerator:
    """Core DXF file generation and management"""
    
    def __init__(self, dxf_version: str = "R2010", units: str = "Meters"):
        self.dxf_version = dxf_version
        self.units = units
        self.drawing = None
        self.layers = {}
        self.logger = get_logger(__name__)
        
        # Standard architectural layers
        self.standard_layers = {
            'WALLS': {'color': 1, 'linetype': 'CONTINUOUS', 'lineweight': 50},      # Red
            'DOORS': {'color': 2, 'linetype': 'CONTINUOUS', 'lineweight': 25},      # Yellow
            'WINDOWS': {'color': 3, 'linetype': 'CONTINUOUS', 'lineweight': 25},    # Green
            'ROOMS': {'color': 4, 'linetype': 'CONTINUOUS', 'lineweight': 13},      # Cyan
            'DIMENSIONS': {'color': 7, 'linetype': 'CONTINUOUS', 'lineweight': 13}, # White
            'TEXT': {'color': 7, 'linetype': 'CONTINUOUS', 'lineweight': 13},       # White
            'FURNITURE': {'color': 6, 'linetype': 'CONTINUOUS', 'lineweight': 13},  # Magenta
            'CIRCULATION': {'color': 5, 'linetype': 'CONTINUOUS', 'lineweight': 25}, # Blue
            'CONSTRUCTION': {'color': 8, 'linetype': 'CENTER', 'lineweight': 13},    # Dark Gray
            'ANNOTATIONS': {'color': 9, 'linetype': 'CONTINUOUS', 'lineweight': 13}  # Light Gray
        }
    
    def create_drawing(self, title: str = "Floor Plan") -> bool:
        """Create new DXF drawing with standard setup"""
        try:
            self.drawing = ezdxf.new(dxfversion=self.dxf_version)
            
            # Set up drawing properties
            self.drawing.header['$INSUNITS'] = self._get_units_code()
            self.drawing.header['$MEASUREMENT'] = 1  # Metric
            self.drawing.header['$LUNITS'] = 2  # Decimal
            self.drawing.header['$LUPREC'] = 3  # Decimal precision
            self.drawing.header['$AUNITS'] = 1  # Decimal degrees
            self.drawing.header['$AUPREC'] = 2  # Angle precision
            
            # Set title block attributes in drawing header
            self.drawing.header['$PROJECTNAME'] = title
            
            # Create standard layers
            self._setup_layers()
            
            self.logger.info(f"Created new DXF drawing: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create DXF drawing: {e}")
            return False
    
    def _get_units_code(self) -> int:
        """Get ezdxf units code for specified units"""
        units_mapping = {
            'Inches': 1,
            'Feet': 2,
            'Miles': 3,
            'Millimeters': 4,
            'Centimeters': 5,
            'Meters': 6,
            'Kilometers': 7,
            'Microinches': 8,
            'Mils': 9,
            'Yards': 10,
            'Angstroms': 11,
            'Nanometers': 12,
            'Microns': 13,
            'Decimeters': 14,
            'Decameters': 15,
            'Hectometers': 16,
            'Gigameters': 17,
            'Astronomical units': 18,
            'Light years': 19,
            'Parsecs': 20
        }
        return units_mapping.get(self.units, 6)  # Default to Meters
    
    def _setup_layers(self):
        """Create standard architectural layers"""
        for layer_name, properties in self.standard_layers.items():
            layer = self.drawing.layers.new(
                name=layer_name,
                dxfattribs={
                    'color': properties['color'],
                    'linetype': properties['linetype'],
                    'lineweight': properties['lineweight']
                }
            )
            self.layers[layer_name] = layer
    
    def add_layer(self, name: str, color: int = 7, linetype: str = 'CONTINUOUS', lineweight: int = 13) -> bool:
        """Add custom layer"""
        try:
            if name in self.layers:
                self.logger.warning(f"Layer '{name}' already exists")
                return False
            
            layer = self.drawing.layers.new(
                name=name,
                dxfattribs={
                    'color': color,
                    'linetype': linetype,
                    'lineweight': lineweight
                }
            )
            self.layers[name] = layer
            self.logger.info(f"Added layer: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add layer '{name}': {e}")
            return False
    
    def add_wall(
        self, 
        start_point: Tuple[float, float], 
        end_point: Tuple[float, float], 
        thickness: float = 0.2,
        layer: str = 'WALLS'
    ) -> Optional[entities.LWPolyline]:
        """Add wall to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            start = validate_point(start_point)
            end = validate_point(end_point)
            
            msp = self.drawing.modelspace()
            
            # Calculate wall offsets for thickness
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx**2 + dy**2)**0.5
            
            if length == 0:
                raise ValueError("Wall start and end points cannot be the same")
            
            # Perpendicular direction
            perp_x = -dy / length * thickness / 2
            perp_y = dx / length * thickness / 2
            
            # Create wall as closed polyline
            wall_points = [
                (start[0] + perp_x, start[1] + perp_y),
                (end[0] + perp_x, end[1] + perp_y),
                (end[0] - perp_x, end[1] - perp_y),
                (start[0] - perp_x, start[1] - perp_y)
            ]
            
            wall = msp.add_lwpolyline(
                points=wall_points,
                close=True,
                dxfattribs={
                    'layer': layer,
                    'lineweight': 50
                }
            )
            
            self.logger.info(f"Added wall from {start} to {end}")
            return wall
            
        except Exception as e:
            self.logger.error(f"Failed to add wall: {e}")
            return None
    
    def add_door(
        self, 
        position: Tuple[float, float], 
        width: float = 0.8,
        angle: float = 0,
        door_type: str = 'single',
        layer: str = 'DOORS'
    ) -> Optional[entities.LWPolyline]:
        """Add door to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            pos = validate_point(position)
            
            # Create door opening
            msp = self.drawing.modelspace()
            
            if door_type == 'single':
                # Single door - simple arc
                half_width = width / 2
                
                # Door arc (90 degree swing)
                door_arc = msp.add_arc(
                    center=pos,
                    radius=width,
                    start_angle=angle,
                    end_angle=angle + 90,
                    dxfattribs={'layer': layer}
                )
                
                # Door swing line
                end_x = pos[0] + width * math.cos(math.radians(angle + 90))
                end_y = pos[1] + width * math.sin(math.radians(angle + 90))
                
                swing_line = msp.add_line(
                    start=pos,
                    end=(end_x, end_y),
                    dxfattribs={'layer': layer}
                )
                
                # Door opening indicators
                start_x = pos[0] - half_width * math.cos(math.radians(angle))
                start_y = pos[1] - half_width * math.sin(math.radians(angle))
                end_x = pos[0] + half_width * math.cos(math.radians(angle))
                end_y = pos[1] + half_width * math.sin(math.radians(angle))
                
                opening = msp.add_line(
                    start=(start_x, start_y),
                    end=(end_x, end_y),
                    dxfattribs={
                        'layer': 'CONSTRUCTION',
                        'linetype': 'CENTER'
                    }
                )
                
            elif door_type == 'double':
                # Double door
                half_width = width / 4
                
                # Left door
                left_arc = msp.add_arc(
                    center=pos,
                    radius=width / 2,
                    start_angle=angle,
                    end_angle=angle + 90,
                    dxfattribs={'layer': layer}
                )
                
                # Right door
                right_center = (
                    pos[0] + width / 2 * math.cos(math.radians(angle)),
                    pos[1] + width / 2 * math.sin(math.radians(angle))
                )
                right_arc = msp.add_arc(
                    center=right_center,
                    radius=width / 2,
                    start_angle=angle + 180,
                    end_angle=angle + 270,
                    dxfattribs={'layer': layer}
                )
            
            self.logger.info(f"Added {door_type} door at {pos}")
            return door_arc if door_type == 'single' else left_arc
            
        except Exception as e:
            self.logger.error(f"Failed to add door: {e}")
            return None
    
    def add_window(
        self, 
        start_point: Tuple[float, float], 
        end_point: Tuple[float, float], 
        width: float = 1.2,
        sill_height: float = 1.0,
        layer: str = 'WINDOWS'
    ) -> Optional[entities.Line]:
        """Add window to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            start = validate_point(start_point)
            end = validate_point(end_point)
            
            msp = self.drawing.modelspace()
            
            # Window line
            window = msp.add_line(
                start=start,
                end=end,
                dxfattribs={'layer': layer}
            )
            
            # Window opening indicators (above and below)
            offset = 0.1
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                # Perpendicular offset
                perp_x = -dy / length * offset
                perp_y = dx / length * offset
                
                # Top line
                top_start = (start[0] + perp_x, start[1] + perp_y)
                top_end = (end[0] + perp_x, end[1] + perp_y)
                top_line = msp.add_line(
                    start=top_start,
                    end=top_end,
                    dxfattribs={'layer': 'CONSTRUCTION'}
                )
                
                # Bottom line
                bottom_start = (start[0] - perp_x, start[1] - perp_y)
                bottom_end = (end[0] - perp_x, end[1] - perp_y)
                bottom_line = msp.add_line(
                    start=bottom_start,
                    end=bottom_end,
                    dxfattribs={'layer': 'CONSTRUCTION'}
                )
            
            self.logger.info(f"Added window from {start} to {end}")
            return window
            
        except Exception as e:
            self.logger.error(f"Failed to add window: {e}")
            return None
    
    def add_room(
        self, 
        polygon_points: List[Tuple[float, float]], 
        room_name: str = "",
        layer: str = 'ROOMS'
    ) -> Optional[entities.LWPolyline]:
        """Add room polygon and label"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            if len(polygon_points) < 3:
                raise ValueError("Room polygon must have at least 3 points")
            
            validated_points = [validate_point(p) for p in polygon_points]
            
            msp = self.drawing.modelspace()
            
            # Add room polygon
            room = msp.add_lwpolyline(
                points=validated_points,
                close=True,
                dxfattribs={'layer': layer}
            )
            
            # Add room label if provided
            if room_name:
                # Calculate room centroid for label placement
                centroid_x = sum(p[0] for p in validated_points) / len(validated_points)
                centroid_y = sum(p[1] for p in validated_points) / len(validated_points)
                
                text = msp.add_text(
                    text=room_name,
                    dxfattribs={
                        'layer': 'TEXT',
                        'height': 0.3,
                        'style': 'Standard'
                    }
                )
                # Set text position and alignment
                text.dxf.insert = (centroid_x, centroid_y)
                text.dxf.halign = 1  # Center alignment
                text.dxf.valign = 2  # Middle alignment
            
            self.logger.info(f"Added room '{room_name}' with {len(validated_points)} vertices")
            return room
            
        except Exception as e:
            self.logger.error(f"Failed to add room: {e}")
            return None
    
    def add_dimension(
        self, 
        start_point: Tuple[float, float], 
        end_point: Tuple[float, float], 
        text_point: Tuple[float, float],
        dimension_type: str = 'linear',
        layer: str = 'DIMENSIONS'
    ) -> Optional[entities.Dimension]:
        """Add dimension to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            start = validate_point(start_point)
            end = validate_point(end_point)
            text = validate_point(text_point)
            
            msp = self.drawing.modelspace()
            
            if dimension_type == 'linear':
                dimension = msp.add_linear_dim(
                    base=start,
                    p1=end,
                    p2=text,
                    dxfattribs={'layer': layer}
                )
            elif dimension_type == 'aligned':
                dimension = msp.add_aligned_dim(
                    p1=start,
                    p2=end,
                    dimlinepoint=text,
                    dxfattribs={'layer': layer}
                )
            else:
                raise ValueError(f"Unsupported dimension type: {dimension_type}")
            
            dimension.render()
            
            self.logger.info(f"Added {dimension_type} dimension")
            return dimension
            
        except Exception as e:
            self.logger.error(f"Failed to add dimension: {e}")
            return None
    
    def add_text(
        self, 
        text: str, 
        position: Tuple[float, float], 
        height: float = 0.3,
        rotation: float = 0,
        layer: str = 'TEXT'
    ) -> Optional[entities.Text]:
        """Add text to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            pos = validate_point(position)
            
            msp = self.drawing.modelspace()
            
            text_entity = msp.add_text(
                text=text,
                dxfattribs={
                    'layer': layer,
                    'height': height,
                    'rotation': rotation
                }
            )
            text_entity.set_pos(pos)
            
            self.logger.info(f"Added text: '{text}' at {pos}")
            return text_entity
            
        except Exception as e:
            self.logger.error(f"Failed to add text: {e}")
            return None
    
    def add_block(
        self, 
        block_name: str, 
        position: Tuple[float, float],
        entities: List[Dict[str, Any]] = None,
        layer: str = 'FURNITURE'
    ) -> Optional[entities.Insert]:
        """Add block to drawing"""
        try:
            if not self.drawing:
                raise ValueError("No drawing created. Call create_drawing() first.")
            
            if layer not in self.layers:
                self.add_layer(layer)
            
            pos = validate_point(position)
            
            # Create block if it doesn't exist
            if block_name not in self.drawing.blocks:
                block = self.drawing.blocks.new(name=block_name)
                
                # Add entities to block if provided
                if entities:
                    for entity_data in entities:
                        entity_type = entity_data.get('type')
                        
                        if entity_type == 'line':
                            block.add_line(
                                start=entity_data['start'],
                                end=entity_data['end'],
                                dxfattribs={'layer': layer}
                            )
                        elif entity_type == 'circle':
                            block.add_circle(
                                center=entity_data['center'],
                                radius=entity_data['radius'],
                                dxfattribs={'layer': layer}
                            )
                        elif entity_type == 'polyline':
                            block.add_lwpolyline(
                                points=entity_data['points'],
                                close=entity_data.get('close', False),
                                dxfattribs={'layer': layer}
                            )
            
            # Insert block
            msp = self.drawing.modelspace()
            insert = msp.add_blockref(
                name=block_name,
                insert=pos,
                dxfattribs={'layer': layer}
            )
            
            self.logger.info(f"Added block '{block_name}' at {pos}")
            return insert
            
        except Exception as e:
            self.logger.error(f"Failed to add block: {e}")
            return None
    
    def save_drawing(self, filename: str, output_dir: str = "./outputs") -> bool:
        """Save drawing to file"""
        try:
            if not self.drawing:
                raise ValueError("No drawing to save. Create a drawing first.")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Ensure filename has .dxf extension
            if not filename.lower().endswith('.dxf'):
                filename += '.dxf'
            
            filepath = os.path.join(output_dir, filename)
            
            self.drawing.saveas(filepath)
            
            self.logger.info(f"Saved drawing to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save drawing: {e}")
            return False
    
    def get_drawing_info(self) -> Dict[str, Any]:
        """Get information about current drawing"""
        if not self.drawing:
            return {"error": "No drawing loaded"}
        
        msp = self.drawing.modelspace()
        
        # Count entities by layer
        entity_counts = {}
        for entity in msp:
            layer = entity.dxf.layer
            entity_counts[layer] = entity_counts.get(layer, 0) + 1
        
        # Get drawing bounds
        try:
            bounds = msp.bounds
            drawing_bounds = {
                "min_x": bounds[0][0] if bounds else 0,
                "min_y": bounds[0][1] if bounds else 0,
                "max_x": bounds[1][0] if bounds else 0,
                "max_y": bounds[1][1] if bounds else 0
            }
        except:
            drawing_bounds = {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0}
        
        return {
            "dxf_version": self.dxf_version,
            "units": self.units,
            "layers": list(self.layers.keys()),
            "entity_counts": entity_counts,
            "bounds": drawing_bounds,
            "total_entities": sum(entity_counts.values())
        }


# Import math for door calculations
import math