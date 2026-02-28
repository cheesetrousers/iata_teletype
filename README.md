# IATA Teletype System

A teletype message system that builds basic IATA Type B teletype messages, exposes an API, and publishes the payloads to an ordered Google Cloud Pub/Sub topic.

## Prerequisites
- Podman
- `uv` (Installed under your WSL user space)

## 1. Start the Pub/Sub Emulator
You can spin up the mock Google Pub/Sub topic on your WSL environment using Podman natively:
```bash
podman run -d --name pubsub-emulator -p 8085:8085 gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators gcloud beta emulators pubsub start --project=iata-teletype-project --host-port=0.0.0.0:8085
```
Or, if you have `podman-compose` installed, you can use the included configuration:
```bash
podman-compose -f infra/docker-compose.yml up -d
```

## 2. Start the FastAPI System
Start the FastAPI REST Publisher which listens on port `8000`:
```bash
uv run teletype-api
```
The API is available at `POST http://localhost:8000/messages/teletype`.

## 3. Start the Textual Receiver TUI
Open a standalone terminal window and run the TUI to visualize the Pub/Sub stream and test message sending:
```bash
uv run teletype-tui
```

In the UI, you can send messages manually. To load content from a file, type `file:path/to/file.txt` in the body field.

## Testing
Run the full test suite to verify the message builder and API:
```bash
uv run pytest
```
## Context & Guidelines
A detailed context document for AI agents and maintainers is available at [.agent/context.md](.agent/context.md). It includes guidelines on testing with `pytest`, mocking with `monkeypatch`, and configuration management for destination rules.
