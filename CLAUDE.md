# ForgeCode Development Guide

## Commands
- Install: `poetry install`
- Run tests: `poetry run pytest`
- Run single test: `poetry run pytest tests/path/to/test.py::test_function`
- Lint: `poetry run flake8`
- Format: `poetry run black .`
- Run pre-commit hooks: `poetry run pre-commit run --all-files`

## Code Style
- Format with Black (line length=88)
- Use type hints for all function params and return values
- Follow PEP8 naming: snake_case for functions/variables, CamelCase for classes
- Import order: stdlib → third-party → local modules
- Docstrings required for all public functions and classes
- Use explicit error handling with custom exception types
- Return proper type hints for functions that return None
- Validate inputs with jsonschema for schema validation
- Use hashlib for caching mechanisms in the code persistence layer