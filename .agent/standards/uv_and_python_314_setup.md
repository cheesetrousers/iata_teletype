# Development with UV and Python 3.14

To simplify dependencies, environment management, and execution, we use `uv` and target Python 3.14 as the base version.

## Key Toolset: UV

`uv` is an extremely fast Python package manager and resolver. It's used for:
- Environment management (`.venv`)
- Dependency resolution (`pyproject.toml`, `uv.lock`)
- Command execution (`uv run`)

## Project Initialization with UV

1. **Initialize a new project:**
   ```bash
   uv init
   ```
2. **Specify Python 3.14:**
   ```bash
   uv venv -p 3.14
   ```
3. **Add Standard Dependencies:**
   ```bash
   uv add fastapi uvicorn pydantic httpx pytest python-json-logger
   ```

## Standard Execution Commands

- **Run any project scripts:**
  ```bash
  uv run <entry_point_name>
  ```
- **Run the test suite:**
  ```bash
  uv run pytest
  ```

## Rationale
- **Python 3.14:** Use the latest available Python version for performance gains and modern language features.
- **UV Performance:** Reduces environment setup and dependency installation time significantly.
- **`uv run`:** Simplifies script execution by automatically managing the virtual environment and its dependencies.
- **`pyproject.toml`:** A unified metadata file that handles metadata, project dependencies, development tools (like pytest), and CLI entry points.

## Best Practices
- **`[project.scripts]`**: Always map project components to functions within your package structure.
- **`pythonpath`**: Use `[tool.pytest.ini_options]` in `pyproject.toml` to specify `pythonpath = ["src"]` for seamless testing across packages.
