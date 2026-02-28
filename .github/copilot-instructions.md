# GitHub Copilot Instructions: IATA Teletype Project

This document provides context for GitHub Copilot to ensure it provides accurate, consistent, and context-aware code reviews, completions, and suggestions for the `iata_teletype` project.

## 📋 Project Context
The `iata_teletype` project is a Python-based system designed to construct IATA-compliant Type B teletype messages, publish them to Google Cloud Pub/Sub, and visualize the message stream in a retro terminal-styled TUI.

## 🏗️ Technical Architecture
1. **REST API (FastAPI)**: A publisher service that accepts JSON payloads (destination, origin, body, opt tag) and converts them into IATA teletype strings.
2. **Message Builder**: A core logic component that handles strict formatting:
   - **Control Characters**: `SOH` (\x01), `STX` (\x02), `ETX` (\x03), `CR/LF` (\r\n), and optional `EOT` (\x04).
   - **Translation**: Converts payloads to the limited **CCITT5** character set (uppercasing and replacing invalid symbols).
   - **Rule Engine**: Configuration is driven by `config/address_config.json`, keyed by the **last 2 characters** of the destination address.
3. **Pub/Sub Broker**: Uses Google Cloud Pub/Sub (Emulator locally) with **Message Ordering** enabled based on the destination address.
4. **TUI (Textual)**: A retro-styled Subscriber that displays incoming messages and provides an interactive form to send new one. It includes a dynamic configuration window that triggers after 7 characters of destination input.

## ⚖️ Consistency Guidelines (CRITICAL)

### 🧪 Testing & Mocking
- **Framework**: Use `pytest` for all tests.
- **Mocking**: Use the native `monkeypatch` fixture. **NEVER** use `unittest.mock.patch` or other `unittest` based decorators.
- **Fixtures**: Use `pytest.fixture` for reusable test dependencies (like `mock_datetime`).

### 🛠️ Configuration & Feature Flags
- Do not hardcode destination behaviors. All logic like `ccitt5` translation and `eot_enabled` status must be retrieved from `address_config.json` based on the destination suffix.

### 📜 Protocol Compliance
IATA teletype messages are byte-sensitive. Ensure:
- `SOH` always starts the header.
- `STX` transition to body.
- `ETX` signals end of body.
- `EOT` signals end of transmission line if enabled by destination config.

## 🎯 What to look for in Code Reviews
When reviewing PRs, verify:
- New tests follow the `pytest`/`monkeypatch` pattern.
- Configuration lookups correctly use the destination suffix logic.
- The TUI's dynamic lookup logic triggers correctly (at length >= 7).
- Proper safe decoding/representation of control characters in logs (e.g., `<SOH>`, `<STX>`, `<EOT>`).
