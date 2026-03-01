# IATA Teletype Project: Context & Consistency Guidelines

This document serves as a source of truth for maintainers and AI agents working on the `iata_teletype` project. It follows our standardized Python development workflow.

## 1. Project Standards (Master Reference)

### A. Environment & Tooling
- **Python Version**: 3.14 (Base version for performance and modern syntax).
- **Package Manager**: `uv` (Fast dependency resolution and environment management).
- **Standard Execution**: ALWAYS use `uv run <script>` to ensure the correct environment is used.
- **Entry Points**: Major components (API, TUI) are defined in `pyproject.toml` under `[project.scripts]`.

### B. Directory Structure (SRC Layout)
```text
iata_teletype/
├── src/                      # Source package
│   └── message_builder/
├── tui/                      # Test tool (standalone package)
├── tests/                    # External test suite
├── config/                   # Configuration files (address_config.json)
├── infra/                    # Infrastructure / Dev tools (Docker Compose)
├── README.md                 # Project entry point
└── specifications.md         # Detailed project specification
```

### C. Preferred Library Stack
- **FastAPI**: Main REST API framework.
- **Pydantic**: Data validation and type-safe models.
- **HTTPX**: Modern HTTP client (sync/async).
- **Pytest**: Standard testing framework. Use `pythonpath = ["src"]` in `pyproject.toml`.
- **Structured Logging**: Use `python-json-logger` for machine-readable JSON logs in production.

## 2. IATA Teletype Project Specifics

### A. Core Stack Recap
- **Frameworks**: FastAPI, Textual (TUI), `httpx`
- **Broker**: Google Cloud Pub/Sub (Emulator for local dev)

### B. Testing Standards
- **Framework**: ALWAYS use `pytest`. Avoid `unittest`.
- **Mocking**: Prefer the native `monkeypatch` fixture or `pytest-mock` over `unittest.mock`.
- **Fixtures**: Reuse common test setups (like `mock_datetime`) as `pytest.fixture`.

### C. Message Protocol & Configuration
- **Centralized Config**: Destination-specific overrides are stored in `config/address_config.json`.
- **Routing Logic**: Rules are keyed by the last 2 characters of the 7-character IATA destination address.
- **ASCII Control Characters**:
    - `SOH` (\x01), `STX` (\x02), `ETX` (\x03), `EOT` (\x04)
    - `CRLF` (\r\n) for line endings.

### D. TUI Logic
- **Visual Feedback**: The TUI displays destination-specific configuration (CCITT5, EOT status) after 7 characters are entered in the destination field.
- **Log Representation**: Safely represent control characters as `<SOH>`, `<STX>`, etc.
