# Specifications: IATA Teletype Message System

## 1. Project Overview
A system designed to construct IATA-compliant teletype messages from a JSON payload, publish those messages to an ordered Google Cloud Pub/Sub topic, and provide a local Text User Interface (TUI) to visualize the message stream in a retro terminal style.

## 2. Core Components

### A. REST API (Publisher)
- **Framework:** FastAPI (Recommended for speed, validation, and auto-generated docs).
- **Endpoint:** `POST /messages/teletype`
- **Request Payload:**
  ```json
  {
    "destination": "LHRXXBA",
    "origin": "JFKYYBA",
    "tag": "OPTIONAL_TAG",
    "body": "FLIGHT DELAYED DUE TO WEATHER",
    "ordering_key": "OPTIONAL_ORDERING_KEY"
  }
  ```
- **Ordering Key:** The API expects an optional `ordering_key` in the JSON. If no key is provided, the system will default to using the `destination` address as the ordering key.

### B. Message Builder
- Formats the input payload into an ASCII string representing an IATA Teletype message.
- Includes standard Teletype control characters (e.g., `STX` [Start of Text], `ETX` [End of Text], `CR` [Carriage Return], `LF` [Line Feed]).
- The Origin line includes the originator address followed by a space and a GMT timestamp formatted as `DDHHMM`.
- The `tag` (if provided) is placed on a line of its own immediately following the `STX`.
- **Character Set Translation:** Teletype messages use a limited character set (CCITT5). Prior to assembling the output, a translation step is run. By checking against an external JSON configuration file (`address_config.json`), the system retrieves the configuration using the last two characters of the destination address (normalized to uppercase). If the rule dictates CCITT5 encoding (or defaults to true if not found), the system translates the payload to strict CCITT5 format (uppercasing the content and replacing unsupported characters).

**Sample Output String (with visible control characters):**
```text
<SOH><CR><LF>
QU LHRXXBA<CR><LF>
.JFKYYBA 151430<CR><LF>
<STX><CR><LF>
OPTIONAL_TAG<CR><LF>
FLIGHT DELAYED DUE TO WEATHER<CR><LF>
<ETX>
```

### C. Message Broker (Pub/Sub)
- **Technology:** Google Cloud Pub/Sub.
- **Features:** Message ordering enabled.
- **Local Testing:** Integration with the Google Cloud Pub/Sub Emulator to run completely locally without cloud credentials.

### D. TUI Receiver (Subscriber)
- **Framework:** `Textual` (Textualize) for Python.
- **Functionality:** Subscribes to the Pub/Sub emulator topic.
- **UI Design:** A retro-styled layout containing an output subwindow (similar to Toad or a vintage terminal) displaying incoming raw ASCII messages and control characters safely.

---

# Development Plan

## Phase 1: Project Setup & Core Logic
- [X] Initialize Python project structure in `C:\Users\User\.gemini\antigravity\scratch\iata_teletype`.
- [X] Use `uv` to set up the virtual environment, generate `pyproject.toml`, and install dependencies (`fastapi`, `uvicorn`, `google-cloud-pubsub`, `textual`, `pytest`).
- [X] Implement the `IataMessageBuilder` utility to accurately format strings and control characters.

## Phase 2: API & Pub/Sub Integration
- [X] Create a `docker-compose.yml` (or startup script) to launch the Google Cloud Pub/Sub Emulator.
- [X] Implement the FastAPI endpoints and request validation models (Pydantic).
- [X] Integrate the Google Cloud Pub/Sub Python client to publish messages with ordering keys to the emulator.

## Phase 3: Textual TUI App (Receiver & CLI Tester)
- [X] Initialize the Textual application structure.
- [X] Build the layout (headers, scrolling output log pane).
- [X] Implement an **Input Screen/Form** within the Textual app to allow sending sample messages directly via CLI from a file.
- [X] Integrate an asynchronous Pub/Sub subscriber into the Textual app to listen and print messages in real-time.
- [X] Handle displaying raw ASCII control characters cleanly in the console.

## Phase 4: Full System Testing & Polish
- [X] Create robust unit tests using `pytest` for the `IataMessageBuilder` and API routes.
- [X] Verify message ordering and correct control character encoding.
- [X] Polish the Textual UI.

## Phase 5: Beer O'Clock
- [X] Shut down the emulator.
- [X] Close the workspace.
- [X] Celebrate successfully implementing complex IATA logic and testing a fully distributed architecture locally.
