# AI-CAD Automation Backend

Backend system for AI-assisted architectural floor plan generation using ezdxf.

## Installation

```bash
pip install -r requirements.txt
```

## Development Setup

```bash
pip install -e ".[dev]"
```

## Running the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

- `src/ai_agent/`: AI agent framework and reasoning engine
- `src/cad/`: DXF generation and CAD operations
- `src/tools/`: Specialized tools for spatial reasoning and validation
- `src/prompts/`: Prompt engineering and domain knowledge
- `src/utils/`: Utility functions and configuration

## Testing

```bash
pytest tests/
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.