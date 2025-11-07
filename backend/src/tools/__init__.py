"""Tools module initialization"""

from .base import Tool, ToolResult, ToolRegistry, tool_registry
from .geometry_utils import GeometryUtilsTool
from .spatial_reasoning import SpatialReasoningTool
from .design_rules import DesignRulesTool

# Register all available tools
def register_tools():
    """Register all available tools in the global registry"""
    tool_registry.register_tool(GeometryUtilsTool())
    tool_registry.register_tool(SpatialReasoningTool())
    tool_registry.register_tool(DesignRulesTool())

# Auto-register tools on import
register_tools()

__all__ = [
    'Tool',
    'ToolResult',
    'ToolRegistry',
    'tool_registry',
    'GeometryUtilsTool',
    'SpatialReasoningTool',
    'DesignRulesTool',
    'register_tools'
]