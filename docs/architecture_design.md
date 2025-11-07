# Core AI Agent Architecture

## Overview

The AI Agent is the central reasoning component that orchestrates the floor plan generation process. It uses a tool-based architecture to separate reasoning from execution.

## Components

### ArchitecturalAgent
Main agent class that manages the overall workflow and coordinates tool usage.

### ReasoningEngine
Handles decision-making logic and planning processes.

### PromptManager
Manages prompt templates and engineering for optimal AI responses.

## Design Principles

1. **Tool Separation**: AI focuses on reasoning, tools handle execution
2. **Modularity**: Each component can be developed and tested independently
3. **Extensibility**: New tools and capabilities can be added easily
4. **Validation**: Multi-layer validation ensures architectural compliance

## Usage Example

```python
from ai_agent.architecture import ArchitecturalAgent
from tools.spatial_reasoning import SpatialReasoningTool
from cad.dxf_generator import DXFGenerator

# Initialize agent with tools
agent = ArchitecturalAgent()
agent.add_tool(SpatialReasoningTool())
agent.add_tool(DXFGenerator())

# Generate floor plan
requirements = {
    "dimensions": {"width": 10.0, "height": 12.0},
    "rooms": ["bedroom", "kitchen", "living_room"]
}

plan = agent.generate_floor_plan(requirements)
```