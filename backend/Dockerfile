# For both mcp-server and chat, since both using same env and libraries
FROM python:3.11-slim

WORKDIR /app

RUN pip install uv
# Tell uv to use system python via environment variable
# ENV UV_PYTHON=/usr/local/bin/python3
# ENV VIRTUAL_ENV=/app/.venv
# ENV PATH="/app/.venv/bin:$PATH"

# solves module not found
ENV PYTHONPATH=/app 


# layer 1, using this copy before copying entire repo, to make subsequent build faster, as system cache this layer and reuses it.
COPY pyproject.toml .
COPY uv.lock .
RUN uv venv /app/.venv 
RUN uv sync --frozen
COPY . .