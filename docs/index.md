# craft-suite-api

ArtCraft **API + MCP Server** using the connector SDK — a
typed, action-routed connector.

!!! info "Official documentation"
    This site is the canonical reference for `craft-suite-api`, maintained alongside
    the source. Package and image releases remain unverified.

![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Knuckles-Team/craft-suite-api/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/craft-suite-api)

## Overview

`craft-suite-api` wraps the target service with typed, deterministic MCP tools.

Tools resolve `CRAFT_SUITE_API_BASE_URL`, `CRAFT_SUITE_API_TOKEN_REF`, and the SDK TLS
profile when invoked. Discovery requires no vendor credentials or live service.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — source environment and the unqualified local-source image recipe.
- :material-server-network: **[Deployment](deployment.md)** — run local transports or connect through an authenticated TLS ingress.
- :material-console: **[Usage](usage.md)** — the MCP tools, the Python client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy the target service with Docker.
- :material-sitemap: **[Overview](overview.md)** — the action-routed tool surface and architecture.
- :material-graph: **[Concepts](concepts.md)** — the CONCEPT ID registry.

</div>
