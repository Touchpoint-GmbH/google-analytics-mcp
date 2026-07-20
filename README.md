# Google Analytics MCP Server (Experimental)

[![PyPI version](https://img.shields.io/pypi/v/analytics-mcp.svg)](https://pypi.org/project/analytics-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub branch check runs](https://img.shields.io/github/check-runs/googleanalytics/google-analytics-mcp/main)](https://github.com/googleanalytics/google-analytics-mcp/actions?query=branch%3Amain++)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/analytics-mcp)](https://pypi.org/project/analytics-mcp/)
[![GitHub stars](https://img.shields.io/github/stars/googleanalytics/google-analytics-mcp?style=social)](https://github.com/googleanalytics/google-analytics-mcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/googleanalytics/google-analytics-mcp?style=social)](https://github.com/googleanalytics/google-analytics-mcp/network/members)
[![YouTube Video Views](https://img.shields.io/youtube/views/PT4wGPxWiRQ)](https://www.youtube.com/watch?v=PT4wGPxWiRQ)

This repo contains the source code for running a local
[MCP](https://modelcontextprotocol.io) server that interacts with APIs for
[Google Analytics](https://support.google.com/analytics).

Join the discussion and ask questions in the
[🤖-analytics-mcp channel](https://discord.com/channels/971845904002871346/1398002598665257060)
on Discord.

## Tools 🛠️

The server uses the
[Google Analytics Admin API](https://developers.google.com/analytics/devguides/config/admin/v1)
and
[Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
to provide several
[Tools](https://modelcontextprotocol.io/docs/concepts/tools) for use with LLMs.

### Retrieve account and property information 🟠

- `get_account_summaries`: Retrieves information about the user's Google
  Analytics accounts and properties.
- `get_property_details`: Returns details about a property.
- `list_google_ads_links`: Returns a list of links to Google Ads accounts for
  a property.

### Run core reports 📙

- `run_report`: Runs a Google Analytics report using the Data API.
- `run_funnel_report`: Runs a Google Analytics funnel report using the Data API.
- `get_custom_dimensions_and_metrics`: Retrieves the custom dimensions and
  metrics for a specific property.

### Run realtime reports ⏳

- `run_realtime_report`: Runs a Google Analytics realtime report using the
  Data API.

## Setup instructions 🔧

✨ Watch the [Google Analytics MCP Setup
Tutorial](https://youtu.be/nS8HLdwmVlY) on YouTube for a step-by-step
walkthrough of these instructions.

[![Watch the video](https://img.youtube.com/vi/nS8HLdwmVlY/mqdefault.jpg)](https://www.youtube.com/watch?v=nS8HLdwmVlY)

Setup involves the following steps:

1.  Configure Python.
1.  Configure credentials for Google Analytics.
1.  Configure Gemini.

### Configure Python 🐍

[Install pipx](https://pipx.pypa.io/stable/#install-pipx).

### Enable APIs in your project ✅

[Follow the instructions](https://support.google.com/googleapi/answer/6158841)
to enable the following APIs in your Google Cloud project:

- [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
- [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

### Configure credentials 🔑

This fork authenticates each user with their **personal Google account** via
OAuth 2.0. It runs as a remote streamable-HTTP server; the MCP connector walks
the user through Google's consent screen, and every tool call runs with that
user's Google Analytics permissions. The account must already have access to
the GA4 properties it should read.

1.  In your Google Cloud project, create an **OAuth 2.0 Client ID** of type
    *Web application* (APIs & Services > Credentials). See
    [Manage OAuth Clients](https://support.google.com/cloud/answer/15549257).

1.  Add the following **Authorized redirect URI**, where `BASE_URL` is the
    public HTTPS URL of your deployment:

    ```
    <BASE_URL>/auth/callback
    ```

1.  Configure the server via environment variables (see
    [`.env.example`](./.env.example)):

    | Variable | Description |
    | --- | --- |
    | `ANALYTICS_MCP_OAUTH_CLIENT_ID` | OAuth 2.0 client ID |
    | `ANALYTICS_MCP_OAUTH_CLIENT_SECRET` | OAuth 2.0 client secret |
    | `ANALYTICS_MCP_BASE_URL` | Public HTTPS base URL, e.g. `https://ga4-mcp.example.com` |

    The requested scopes are `openid`, `userinfo.email`, `userinfo.profile`,
    and `https://www.googleapis.com/auth/analytics.readonly`.

When both OAuth client variables are set, `analytics-mcp` serves streamable
HTTP at `/mcp`. With them unset it falls back to stdio (for local development),
but tool calls then have no user token and will fail — OAuth is the supported
path for this fork.

### Deploy with Docker 🐳

```shell
docker build -t analytics-mcp .
docker run -p 8000:8000 --env-file .env analytics-mcp
```

### Connect an MCP client

Point your client at the deployed endpoint and let it run the OAuth flow:

```
https://ga4-mcp.example.com/mcp
```

For example, in Claude Code:

```shell
claude mcp add analytics-mcp \
  --scope user \
  --transport http \
  https://ga4-mcp.example.com/mcp
```

## Try it out 🥼

Launch Gemini Code Assist or Gemini CLI and type `/mcp`. You should see
`analytics-mcp` listed in the results.

Here are some sample prompts to get you started:

- Ask what the server can do:

  ```
  what can the analytics-mcp server do?
  ```

- Ask about a Google Analytics property

  ```
  Give me details about my Google Analytics property with 'xyz' in the name
  ```

- Prompt for analysis:

  ```
  what are the most popular events in my Google Analytics property in the last 180 days?
  ```

- Ask about signed-in users:

  ```
  were most of my users in the last 6 months logged in?
  ```

- Ask about property configuration:

  ```
  what are the custom dimensions and custom metrics in my property?
  ```

## Contributing ✨

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).
