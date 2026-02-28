# IATA Teletype Project: Context & Consistency Guidelines

This document serves as a source of truth for maintainers and AI agents working on the `iata_teletype` project.

## 1. Project Overview
A system for constructing IATA-compliant teletype messages, publishing them to Google Cloud Pub/Sub, and visualizing them in a Textual TUI.

### Core Stack
- **Languages**: Python 3.14+
- **Frameworks**: FastAPI, Textual (TUI), `httpx`
- **Broker**: Google Cloud Pub/Sub (Emulator for local dev)
- **Testing**: `pytest`

## 2. Development Principles & Consistency

### Testing Standards
- **Framework**: ALWAYS use `pytest`. Avoid `unittest`.
- **Mocking**: NEVER use `unittest.mock.patch` or other `unittest`-derived decorators.
- **Mocking Tool**: Use the native `monkeypatch` fixture provided by `pytest`.
- **Fixtures**: Reuse common test setups (like `mock_datetime`) as `pytest.fixture` functions in each test file or a `conftest.py`.

### Configuration Management
- **Centralized Config**: Destination-specific overrides (like encoding rules and message flags) MUST be stored in `config/address_config.json`.
- **Destination Suffixes**: Rules are keyed by the last 2 characters of the 7-character IATA destination address (e.g., `BA`, `AA`, `XR`).
- **Config Variables**:
    - `ccitt5`: Boolean. If true, translate text to the limited CCITT5 character set.
    - `eot_enabled`: Boolean. If true, append an EOT string (`\r\n\x04`) to the end of the message.

## 3. Message Protocol Details
IATA teletype messages use strict ASCII control characters:
- `SOH` (\x01): Start of Heading
- `STX` (\x02): Start of Text
- `ETX` (\x03): End of Text
- `EOT` (\x04): End of Transmission (optional based on config)
- `CRLF` (\r\n): Standard line ending.

## 4. TUI Behavior
- **Dynamic Config**: The TUI should display destination-specific configuration (CCITT5 status, EOT status) in a side window as the user types.
- **Trigger**: The config window should only update after at least **7 characters** have been input into the destination field.
- **Logs**: The message log must safely decode and represent control characters (e.g., `<SOH>`, `<STX>`, `<EOT>`) for human readability.
