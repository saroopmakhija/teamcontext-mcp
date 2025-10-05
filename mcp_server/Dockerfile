FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# 🔧 Use the env var your code actually reads
# On Docker Desktop, this points to the host machine.
ENV BACKEND_URL="http://host.docker.internal"
ENV PORT="8000"

COPY . .
EXPOSE 8001
CMD ["uv", "run", "mcp_server.py"]
