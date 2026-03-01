# Preferred Libraries and Coding Patterns

To ensure consistency and high quality, we prefer a modern, type-safe stack.

## Core Library Stack

- **FastAPI**: Use instead of Flask/Django for RESTful APIs. It provides high performance, automatic OpenAPI documentation, and native async support.
- **Pydantic**: Use for data validation, serialization, and settings management (e.g., `BaseModel`, `Settings`).
- **HTTPX**: Prefer over `requests` for HTTP clients. It supports both synchronous and asynchronous operations and is more modern.
- **Pytest**: The standard for testing. Focus on using fixtures and parameterized tests.
- **JSON Logging**: Use structured logging (e.g., via `python-json-logger`) for all production logs. This improves observability and allows for easier searching/parsing by logging backends.

## Application Patterns

- **Dependency Injection**: Use FastAPI's builtin dependency injection system for managing database sessions, auth, and configuration.
- **Async First**: Default to asynchronous code for I/O bound operations (API calls, database queries).
- **Type Hinting**: Always use static type hints for function arguments and return values.
- **Structured Error Responses**: Use Pydantic models to define standard error response formats for all API endpoints.

## JSON Logging Example

Configure the root logger with a JSON formatter:
```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```
