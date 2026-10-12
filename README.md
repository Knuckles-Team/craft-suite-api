# ArtCraft API connector

**Work in progress. This scaffold is not released or deployment-ready.**

`artcraft-api` prepares an API client and MCP entry point for the
[ArtCraft backend](https://github.com/storytold/artcraft-services). Provider
operations, authentication and source mappings still require validation against
the backend's authoritative OpenAPI document and an isolated running service.
The generated `status` and `info` actions are starter examples, not verified
ArtCraft API operations. Do not use them against production services.

## Overview

This repository targets the HTTP backend in `storytold/artcraft-services`.
The desktop editor suite in [storytold/artcraft](https://github.com/storytold/artcraft)
and its native MCP integrations are a separate integration surface. This
scaffold does not provide verified desktop editing or media-generation tools.

The shared `agent-connector-sdk` owns transport, credential references, TLS,
MCP registration, content publication and ingestion. This package will own
reviewed ArtCraft operations and mappings. Starter skills, prompts and ontology
are included for review; their presence does not establish domain completeness.

## Validation status

The scaffold was generated from `universal-skills` revision
`a41b3ae9cb75c4e42a25a916eb1b3d97a28dff74` on 2026-10-12.
The generation date is not a release or delivery date.

- Two baseline generations matched all 141 files, including 34 hidden-path
  files, by SHA-256 and Git executable mode.
- Rendering the canonical generic template with explicit literal substitutions,
  updating the ontology digest and running the canonical readiness generator
  produced the same complete baseline. This README is a project-owned edit.
- Python/TOML parsing, the static connector contract and the canonical shared
  theme comparison passed on the baseline.
- Full package checks, current dynamic SDK discovery/schema validation and
  rendered-site acceptance remain incomplete. A queued CI job is not a pass.
- No authoritative backend OpenAPI export has been obtained for conversion.
  Live authentication, read operations and isolated write fixtures are untested.
- No package release, service deployment or credential provisioning is claimed.

The [capability specification](specs/artcraft-api/spec.md) and its five
requirements remain `SPECIFIED`, with no landing or verification receipts.
See the [local delivery documentation](docs/spec-delivery.md).

## Quick start

For source inspection and local development, clone this repository and install
from the checkout in an approved development environment:

```bash
git clone https://github.com/Knuckles-Team/artcraft-api.git
cd artcraft-api
python -m pip install -e ".[mcp]"
```

The generated console entry point is `artcraft-mcp`. Its stdio startup command
is shown below for future validation; running it does not establish that the
starter actions match the ArtCraft backend:

```bash
artcraft-mcp
```

There is no verified PyPI release or published documentation site for this
pilot. Use the repository's source and local documentation while checks remain
incomplete.

## Architecture

```text
caller → MCP entry point → operation router → API client → ArtCraft backend
                           └── packaged skills, prompts, ontology and manifest
source observations → connector mappings → shared SDK ingestion service
```

`artcraft_api/api/` owns provider requests; `artcraft_api/mcp/` adapts reviewed
operations to tools. The current example routes and ontology resource type
must be replaced or confirmed from authoritative provider contracts.

<!-- MCP-TOOLS-TABLE:START -->
<!-- MCP-TOOLS-TABLE:END -->

## MCP configuration

Keep endpoint, credential and TLS references in operator configuration. Never
commit resolved credentials or private service endpoints. Network exposure
requires separately reviewed authentication and transport configuration.

```json
{
  "mcpServers": {
    "artcraft-mcp": {
      "command": "artcraft-mcp",
      "args": [],
      "env": {"SYSTEMTOOL": "true"}
    }
  }
}
```

<!-- MCP-CONFIG-EXAMPLES:START -->
<!-- MCP-CONFIG-EXAMPLES:END -->

The generated `.env.example` documents setting names with empty credential
values. Deployment manifests for a private service belong outside this source
repository. Creating this scaffold does not grant access to any service.

## Documentation

- [Architecture](docs/architecture.md)
- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Deployment template](docs/deployment.md)
- [Platform integration](docs/platform.md)
- [Concept registry](docs/concepts.md)
- [Requirements and acceptance targets](specs/artcraft-api/requirements.md)

These generated guides describe the intended contract. They are not evidence
of a tested ArtCraft deployment or completed integration. The Pages workflow
and shared theme remain in place for later publication checks.

## Development

Use an isolated branch and the approved existing toolchain. The normal checks
remain required before completion:

```bash
python scripts/check_connector_contract.py . --package artcraft_api
python scripts/generate_tool_schemas.py
python scripts/generate_tool_schemas.py --check
python scripts/generate_agent_readiness.py --root . --check
python -m pytest tests -q
pre-commit run --all-files
mkdocs build --strict
```

Do not bypass pending or failing gates. Keep write tests isolated, and begin
live service validation with read-only operations after access is authorized.
See [AGENTS.md](AGENTS.md) for ownership and contribution rules.

## License

MIT; see [LICENSE](LICENSE).
