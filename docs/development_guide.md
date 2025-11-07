# Development Guide

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Virtual environment recommended

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd AI-CAD
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

## Development Workflow

### Code Style
- Use Black for formatting: `black src/`
- Use flake8 for linting: `flake8 src/`
- Use mypy for type checking: `mypy src/`

### Testing
- Run all tests: `pytest tests/`
- Run unit tests: `pytest tests/unit/`
- Run integration tests: `pytest tests/integration/`
- Run with coverage: `pytest --cov=src tests/`

### Project Structure Guidelines

#### Adding New Tools
1. Create tool class in `src/tools/`
2. Inherit from base `Tool` class
3. Implement `execute()` and `validate_parameters()` methods
4. Add unit tests in `tests/unit/tools/`

#### Adding New CAD Operations
1. Extend `DXFGenerator` or create new entity managers
2. Follow ezdxf best practices
3. Add validation for geometric constraints
4. Test with various DXF versions

#### Prompt Engineering
1. Add templates to `src/prompts/templates.py`
2. Include domain knowledge in `src/prompts/domain_knowledge.py`
3. Test prompts with various requirement scenarios
4. Monitor and refine based on AI performance

## Environment Variables

Create `.env` file in backend root:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:password@localhost/aicad
LOG_LEVEL=INFO
```

## Debugging

### Logging
- Logs are configured in `src/utils/logger.py`
- Use structured logging with context
- Different log levels for development vs production

### Common Issues
1. **DXF Compatibility**: Ensure ezdxf version supports required features
2. **AI API Limits**: Monitor token usage and rate limits
3. **Memory Usage**: Large floor plans may require optimization
4. **Geometric Precision**: Use appropriate tolerance for calculations

## Performance Optimization

### Caching
- Redis for AI responses and intermediate results
- File-based caching for generated DXF files

### Async Operations
- Use async/await for I/O operations
- Parallel processing for independent calculations

### Memory Management
- Process large geometries in chunks
- Clean up temporary objects promptly