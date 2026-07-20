# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

# Install the package plus the HTTP server runtime dependencies.
COPY . /app
RUN pip install --no-cache-dir . "uvicorn[standard]"

# Run as a non-root user.
RUN useradd -m app && chown -R app /app
USER app

ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

CMD ["python", "-m", "analytics_mcp.http_server"]
