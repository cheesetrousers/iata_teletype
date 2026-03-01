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
## Phase 6: EOT Support & TUI Enhancement
- [X] Add `eot_enabled` flag to `address_config.json` (defaults to `false`).
- [X] Define EOT string as `<CR><LF><EOT>` (where EOT is `\x04`).
- [X] Update `IataMessageBuilder` to append the EOT string if configured for the destination.
- [X] Enhance TUI with a dynamic configuration display window:
    - [X] Triggers after 7 characters of destination have been entered.
    - [X] Shows current encoding (CCITT5) and EOT settings for that destination suffix.
- [X] Expand test suite with test cases involving EOT-enabled destinations.
- [X] Validate end-to-end flow from API to TUI with EOT characters.

## Phase 7: Monitoring & Observability
- [ ] Implement a `/health` endpoint in the FastAPI service to monitor system readiness.
- [ ] Add structured JSON logging across the API and Message Builder for better log aggregation.
- [ ] Integrate a **Heartbeat Mechanism** in the TUI to visualize the health of the Pub/Sub subscriber connection.
- [ ] (Optional) Add Prometheus metrics to track message throughput and delivery latency.

---

## Phase 8: Containerization & Remote Deployment
- [ ] **Dockerfile Creation**: Develop a multi-stage Dockerfile targeting a minimal Python 3.14-slim runtime.
- [ ] **Pub/Sub Remote Deployment**: Deploy the Google Cloud Pub/Sub emulator on the Synology NAS using Podman/Docker to serve as the remote message broker for both the remote API and local TUI.
- [ ] **Nexus Integration**: Configure the local Nexus repository on the Synology NAS as a private Docker registry.
- [ ] **Local Build Pipeline**: Create a Jenkinsfile or a local build script to automate the `docker build`, `tag`, and `push` to the local Nexus registry.
- [ ] **Synology Deployment**: Deploy the FastAPI message builder on the NAS using the Synology Container Manager (Docker) plugin, pulling directly from the local Nexus.
- [ ] **Environment Configuration**: Set up environment variables within the container (e.g., `PROJECT_ID`, `PUBSUB_EMULATOR_HOST`) to ensure the remote container can communicate with the Pub/Sub emulator.
- [ ] **Remote Verification**: Validate that the remote API is reachable and correctly publishes messages from the NAS back to the local subscriber (or a remote one).
- [ ] **Security**: Ensure no exposure to public GitHub (use local registry and local Jenkins/webhook).

---

# Maintenance Backlog
- [ ] **Config Caching**: Refactor `IataMessageBuilder.load_config` to cache the configuration in a class variable to avoid frequent disk I/O, especially for the TUI's dynamic lookup feature.
- [ ] **Address Validation**: Add stricter validation for the 7-character IATA address format.
- [ ] **Resilience**: Implement auto-reconnect logic for the Pub/Sub subscriber in case of emulator timeout or network issues.
