FROM python:3.11-slim

# Fast installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# Copy app code
COPY . .

# Expose the SAME port the server binds
EXPOSE 8001

# Start the MCP server
CMD ["uv", "run", "mcp_server.py"]
