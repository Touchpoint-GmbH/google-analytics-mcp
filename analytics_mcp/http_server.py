# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Streamable-HTTP entry point for remote deployment (e.g. Claude connectors).

The upstream ``analytics_mcp.server`` only speaks stdio. This module wraps the
same low-level MCP server (``coordinator.app``) in a Starlette/uvicorn ASGI app
so it can be reached over HTTPS behind a reverse proxy (Traefik/Dokploy).

The MCP endpoint is served at ``/mcp``. A lightweight ``/healthz`` route is
exposed for container health checks.
"""

import contextlib
import os
from collections.abc import AsyncIterator

import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

import analytics_mcp.coordinator as coordinator


class BearerAuth:
    """Optional shared-secret gate.

    Only enforced when ``MCP_AUTH_TOKEN`` is set. Requests to ``/mcp`` must then
    carry ``Authorization: Bearer <token>``. The health check stays public so
    the platform can probe the container without the secret.
    """

    def __init__(self, app: Starlette) -> None:
        self.app = app
        self.token = os.environ.get("MCP_AUTH_TOKEN")

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] == "http" and self.token:
            path = scope.get("path", "")
            if path.startswith("/mcp"):
                headers = dict(scope.get("headers") or [])
                provided = headers.get(b"authorization", b"").decode()
                if provided != f"Bearer {self.token}":
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 401,
                            "headers": [
                                (b"content-type", b"application/json")
                            ],
                        }
                    )
                    await send(
                        {
                            "type": "http.response.body",
                            "body": b'{"error":"unauthorized"}',
                        }
                    )
                    return
        await self.app(scope, receive, send)


def build_app() -> Starlette:
    """Builds the Starlette app that serves the MCP server over HTTP."""
    # stateless=True: each request is self-contained (ideal for connectors and
    # trivial horizontal scaling).
    #
    # security_settings left as the SDK default: the DNS-rebinding host check
    # stays OFF. Behind Traefik the incoming Host header is the public domain,
    # so enabling the check without an explicit allow-list would reject proxied
    # requests with HTTP 421. For a proxied server-to-server endpoint this
    # protection is not the relevant threat model. To enable it, pass
    # ``security_settings`` with ``allowed_hosts=["ga4-mcp.touchpoint.agency"]``.
    manager = StreamableHTTPSessionManager(
        app=coordinator.app,
        json_response=False,
        stateless=True,
    )

    async def handle_mcp(scope: Scope, receive: Receive, send: Send) -> None:
        await manager.handle_request(scope, receive, send)

    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @contextlib.asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        async with manager.run():
            yield

    return Starlette(
        routes=[
            Route("/healthz", endpoint=healthz, methods=["GET"]),
            Mount("/mcp", app=handle_mcp),
        ],
        lifespan=lifespan,
    )


app = BearerAuth(build_app())


def main() -> None:
    """Runs the HTTP server via uvicorn."""
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )


if __name__ == "__main__":
    main()
