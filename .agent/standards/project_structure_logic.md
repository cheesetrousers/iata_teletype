# Standardized Project Structure (Python)

To ensure consistency, readability, and scalability across projects, we follow a strict directory layout based on a `src` layout.

## Directory Structure Logic

```text
project_root/
├── src/                      # Main source package(s)
│   └── <package_name>/
│       ├── __init__.py
│       ├── core_logic.py
│       └── components/       # Component-specific subpackages
├── tests/                    # External test suite
│   ├── __init__.py
│   ├── test_logic.py
│   └── test_integration.py
├── config/                   # Configuration files (separate from code)
│   └── settings.json
├── infra/                    # Infrastructure / Dev Tools (Docker, config, etc.)
│   └── docker-compose.yml
├── README.md                 # Project entry documentation
├── pyproject.toml            # Build system metadata & scripts
└── specifications.md         # Detailed project spec
```

## Rationale
- **SRC Layout:** Prevents accidental import of modules from the root. Ensures that the installed package is what's being tested.
- **`tests/` Outside `src/`:** Keeps test code out of the final distribution artifact.
- **`config/` Separation:** Decouples variables that may change (environment-specific) from the core logic.
- **`infra/`:** Clearly separates secondary developer tools (simulators, containers) from the application.

## Best Practices
- **Custom Scripts:** Define entry points in `pyproject.toml` (`[project.scripts]`) for all major components (APIs, TUIs, CLI tools).
- **Dynamic Pathing:** Use `os.path` or `pathlib` relative to `__file__` to find configuration and resources independently of the execution context.
