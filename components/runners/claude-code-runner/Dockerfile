FROM python:3.11-slim

# Install system dependencies including uv
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV RUNNER_TYPE=claude
ENV HOME=/app
ENV SHELL=/bin/bash
ENV TERM=xterm-256color
ENV UV_SYSTEM_PYTHON=1

# Create working directory
WORKDIR /app

# Copy runner-shell package first
COPY runner-shell /app/runner-shell

# Install runner-shell using uv
RUN cd /app/runner-shell && uv pip install --no-cache .

# Copy claude-runner files including uv.lock
COPY claude-code-runner/pyproject.toml claude-code-runner/uv.lock /app/claude-runner/
COPY claude-code-runner/wrapper.py /app/claude-runner/

# Install claude-runner dependencies using uv.lock
RUN cd /app/claude-runner && uv sync --frozen --no-dev

# OpenShift compatibility
RUN chmod -R g=u /app && chmod -R g=u /usr/local && chmod g=u /etc/passwd

# Default command - run via runner-shell using uv
CMD ["uv", "run", "--frozen", "/app/claude-runner/wrapper.py"]
