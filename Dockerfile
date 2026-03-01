# --- Stage 1: The Build Environment ---
FROM ghcr.io/astral-sh/uv:0.6.1-python3.14-slim AS builder

WORKDIR /app

# Enable bytecode compilation during installation
ENV UV_COMPILE_BYTECODE=1

# Install dependencies into the system site-packages (no .venv)
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv pip install --system --no-cache -r pyproject.toml

# Copy and compile our source code
COPY src/message_builder ./message_builder
COPY config ./config
RUN python -m compileall .

# --- Stage 2: The De Minimis Runtime ---
FROM python:3.14-slim-bookworm

WORKDIR /app

# Copy ONLY the installed packages from the builder's system python
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy ONLY the pre-compiled application code
COPY --from=builder /app /app

# Environment defaults (can be overridden at runtime on Synology)
ENV PUBSUB_EMULATOR_HOST=localhost:8085
ENV PROJECT_ID=iata-teletype-project
ENV PYTHONPATH=/app

EXPOSE 8000

# Start directly with uvicorn
CMD ["uvicorn", "message_builder.api:app", "--host", "0.0.0.0", "--port", "8000"]
