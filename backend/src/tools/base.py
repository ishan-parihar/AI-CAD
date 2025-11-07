"""Base tool interface for AI agent tools"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError
from src.utils import get_logger

logger = get_logger(__name__)


class ToolResult(BaseModel):
    """Standard result format for tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class Tool(ABC):
    """Base class for all AI agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(f"tool.{name}")
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against schema"""
        try:
            schema = self.get_parameters_schema()
            # Basic validation - can be extended with pydantic
            required_params = schema.get('required', [])
            for param in required_params:
                if param not in parameters:
                    raise ValueError(f"Required parameter '{param}' is missing")
            return True
        except Exception as e:
            self.logger.error(f"Parameter validation failed: {e}")
            return False
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for AI agent"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.get_parameters_schema()
        }


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.logger = get_logger(__name__)
    
    def register_tool(self, tool: Tool) -> None:
        """Register a new tool"""
        if tool.name in self.tools:
            self.logger.warning(f"Tool '{tool.name}' already exists, overwriting")
        
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool.get_tool_info() for tool in self.tools.values()]
    
    def execute_tool(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found"
            )
        
        try:
            if not tool.validate_parameters(parameters):
                return ToolResult(
                    success=False,
                    error=f"Invalid parameters for tool '{name}'"
                )
            
            return tool.execute(parameters)
        
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )


# Global tool registry
tool_registry = ToolRegistry()