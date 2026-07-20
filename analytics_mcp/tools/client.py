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

"""Client initialization for the Google Analytics APIs.

Credentials are resolved per request from the access token that FastMCP's OAuth
proxy obtained for the signed-in user. Because every request may belong to a
different user, credentials are intentionally *not* cached across calls.
"""

import threading
from importlib import metadata

from fastmcp.server.dependencies import get_access_token
from google.oauth2.credentials import Credentials
from google.analytics import (
    admin_v1beta,
    data_v1beta,
    admin_v1alpha,
    data_v1alpha,
)
from google.api_core.gapic_v1.client_info import ClientInfo


def _get_package_version_with_fallback():
    """Returns the version of the package.

    Falls back to 'unknown' if the version can't be resolved.
    """
    try:
        return metadata.version("analytics-mcp")
    except:
        return "unknown"


# Client information that adds a custom user agent to all API requests.
_CLIENT_INFO = ClientInfo(
    user_agent=f"analytics-mcp/{_get_package_version_with_fallback()}"
)

# Lock to ensure client creation is thread-safe.
_client_lock = threading.Lock()


def _get_credentials() -> Credentials:
    """Returns credentials built from the current user's OAuth access token.

    The token is provided by FastMCP's OAuth proxy for the request in flight, so
    API calls run with the signed-in user's Google Analytics permissions. The
    user must have been granted access to the relevant GA4 properties.
    """
    token = get_access_token()
    if token is None or not token.token:
        raise RuntimeError(
            "No OAuth access token in the request context. This server "
            "requires per-user authentication via the OAuth proxy; set "
            "ANALYTICS_MCP_OAUTH_CLIENT_ID and ANALYTICS_MCP_OAUTH_CLIENT_SECRET "
            "and connect over streamable HTTP."
        )
    return Credentials(token=token.token)


def create_admin_api_client() -> admin_v1beta.AnalyticsAdminServiceClient:
    """Returns the Google Analytics Admin API client."""
    with _client_lock:
        return admin_v1beta.AnalyticsAdminServiceClient(
            client_info=_CLIENT_INFO, credentials=_get_credentials()
        )


def create_data_api_client() -> data_v1beta.BetaAnalyticsDataClient:
    """Returns the Google Analytics Data API client."""
    with _client_lock:
        return data_v1beta.BetaAnalyticsDataClient(
            client_info=_CLIENT_INFO, credentials=_get_credentials()
        )


def create_admin_alpha_api_client() -> (
    admin_v1alpha.AnalyticsAdminServiceClient
):
    """Returns the Google Analytics Admin API (alpha) client."""
    with _client_lock:
        return admin_v1alpha.AnalyticsAdminServiceClient(
            client_info=_CLIENT_INFO, credentials=_get_credentials()
        )


def create_data_api_alpha_client() -> data_v1alpha.AlphaAnalyticsDataClient:
    """Returns the Google Analytics Data API (Alpha) client."""
    with _client_lock:
        return data_v1alpha.AlphaAnalyticsDataClient(
            client_info=_CLIENT_INFO, credentials=_get_credentials()
        )
