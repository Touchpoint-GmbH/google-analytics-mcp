# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

# Install the package (FastMCP bundles the HTTP server runtime).
COPY . /app
RUN pip install --no-cache-dir .

# Run as a non-root user.
RUN useradd -m app && chown -R app /app
USER app

ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# Serves streamable HTTP when the OAuth client env vars are set (see .env.example).
CMD ["analytics-mcp"]
