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
Or, if you have `podman-compose` installed, you can still use the included `.yml` file:
```bash
podman-compose up -d
```

## 2. Start the FastAPI System
Start the FastAPI REST Publisher which listens on port `8000`:
```bash
uv run uvicorn main:app --reload
```
You can now send POST requests either directly via `curl` or through the interactive TUI.
The API is available at `POST http://localhost:8000/messages/teletype`.

## 3. Start the Textual Receiver TUI
Open a standalone terminal window (or a new Tmux pane) and run the TUI to listen to the Pub/Sub Emulator and send CLI messages safely:
```bash
uv run python tui.py
```
*(Optionally you can run it via `uv run textual run tui.py`)*

In the UI, you can send direct messages. Instead of typing the body manually, enter `file:filename.txt` in the body field to inject the contents of a local file.

## Testing
Run the pytest suite to verify builder functions and formatting strings:
```bash
uv run pytest test_builder.py
```
