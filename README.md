## 1. Setup Environment
Ensure all dependencies are installed and the project is synced so the entry points work:
```bash
uv sync
```

## 2. Start the Pub/Sub Emulator
The system requires the Google Cloud Pub/Sub emulator. Start it via Podman:
```bash
# To create and start the container for the first time:
podman run -d --name pubsub-emulator -p 8085:8085 gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators gcloud beta emulators pubsub start --project=iata-teletype-project --host-port=0.0.0.0:8085

# To start it if it already exists:
podman start pubsub-emulator
```

## 3. Run the API (Publisher)
In a new terminal window, start the FastAPI REST Publisher:
```bash
uv run teletype-api
```
The API serves at `http://localhost:8000`. You can view the auto-generated documentation at `http://localhost:8000/docs`.

## 4. Run the TUI (Receiver/Tester)
In another terminal window, start the Textual-based TUI:
```bash
uv run teletype-tui
```
**Usage Tip**: Enter exactly **7 characters** in the "Dest" field to trigger the dynamic configuration lookup (CCITT5/EOT rules).

## Testing
Run the full pytest suite:
```bash
uv run pytest
```
## Context & Guidelines

Detailed project documentation and standards are maintained in the following files:

- **[specifications.md](specifications.md)**: The primary source of truth for project requirements, core components description, and the multi-phase development plan.
- **[.agent/context.md](.agent/context.md)**: A comprehensive guide for AI agents and maintainers, detailing coding standards, testing practices (using `pytest` and `monkeypatch`), and IATA protocol specifics.
- **[.agent/standards/](.agent/standards/)**: A directory containing our standardized Python development workflows (SRC layout, `uv` integration, and library preferences).
