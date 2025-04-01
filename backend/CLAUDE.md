# Invoice Analyzer Backend Guide

## Commands
- **Start server**: `uvicorn main:app --reload`
- **Tests**: `python3 -m pytest tests/ -v`
- **Run single test**: `python3 -m pytest tests/test_name.py::test_function -v`
- **OpenAI test**: `python3 test_openai.py`
- **Install dependencies**: `python3 -m pip install -r requirements.txt`

## Environment
- Use Python 3.13+
- Store API keys in .env file (not committed to git)
- Use FastAPI for backend services
- Use OpenAI API for document processing

## Code Style
- **Imports**: Group standard library → third party → local imports with blank line separators
- **Formatting**: Use 4 spaces for indentation
- **Types**: Use type hints for function parameters and return values
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use try/except blocks with specific exceptions
- **Docstrings**: Use triple quotes for functions and classes
- **API routes**: Organize endpoints logically with appropriate HTTP methods

## Best Practices
- Handle OpenAI API exceptions explicitly
- Validate data with Pydantic models
- Use HTTPException for API errors with appropriate status codes