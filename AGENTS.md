# AI-CAD Development Guide for Agentic Coding

## Build/Test Commands

### Backend (Python)
```bash
# Development server
cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest tests/                    # Run all tests
pytest tests/test_api.py         # Run single test file
pytest tests/test_api.py::test_health_check  # Run specific test
pytest --cov=src tests/          # Run with coverage

# Code quality
black src/                       # Format code
flake8 src/                      # Lint code
mypy src/                        # Type checking
```

### Frontend (Next.js/TypeScript)
```bash
cd frontend
npm run dev                      # Development server (port 3000)
npm run build                    # Production build
npm run start                    # Production server
npm run lint                     # ESLint
npm run type-check               # TypeScript type checking
npm test                         # Run Jest tests
npm run test:watch              # Jest in watch mode
npm run format                   # Prettier formatting
```

## Code Style Guidelines

### Python (Backend)
- **Formatting**: Use Black (22.0.0+) with default settings
- **Linting**: flake8 with line length 88
- **Types**: Use mypy with strict type checking
- **Imports**: Group imports (stdlib, third-party, local) with blank lines
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Use triple quotes, include parameters and return types
- **Error Handling**: Use specific exceptions, log errors with context
- **Async**: Use async/await for I/O operations, background tasks for long processes

### TypeScript (Frontend)
- **Formatting**: Prettier with Tailwind plugin
- **Linting**: ESLint with Next.js and TypeScript rules
- **Types**: Strict TypeScript, interface over type for objects
- **Imports**: Use @/* path aliases, separate third-party from local imports
- **Naming**: camelCase for variables/functions, PascalCase for components/types
- **Components**: Functional components with hooks, 'use client' directive when needed
- **Error Handling**: Try-catch with proper error types, user-friendly error messages

### General Patterns
- **API Routes**: Use /api/v1/ prefix, return consistent JSON responses
- **Database**: SQLAlchemy ORM with Pydantic models for validation
- **WebSocket**: Real-time updates for plan generation progress
- **DXF Files**: Store in backend/outputs/{plan_id}/ with descriptive names
- **Environment**: Use .env files, never commit secrets
- **Logging**: Structured logging with context, appropriate log levels

### File Organization
- **Backend**: src/{ai_agent,cad,database,tools,utils}/ structure
- **Frontend**: src/{components,hooks,lib,types,app}/ structure
- **Tests**: Mirror source structure, use descriptive test names
- **DXF**: Architectural layer naming (WALLS, DOORS, ROOMS, etc.)

### Key Dependencies
- **Backend**: FastAPI, ezdxf, SQLAlchemy, OpenAI, pytest, black
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, Zustand

### Testing Strategy
- Unit tests for individual components/functions
- Integration tests for API endpoints
- WebSocket testing for real-time features
- DXF validation for generated files
- Always test error paths and edge cases