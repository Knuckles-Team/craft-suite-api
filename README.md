# Craft Suite API connector
## CLI or API | MCP

![PyPI - Version](https://img.shields.io/pypi/v/craft-suite-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/craft-suite-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/craft-suite-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/craft-suite-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/craft-suite-api)
![PyPI - License](https://img.shields.io/pypi/l/craft-suite-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/craft-suite-api)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/craft-suite-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/craft-suite-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/craft-suite-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/craft-suite-api)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/craft-suite-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/craft-suite-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/craft-suite-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/craft-suite-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/craft-suite-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/craft-suite-api)

> **Documentation** — Installation, deployment, and usage across the API, CLI, MCP,
> and A2A agent interfaces are maintained in the
> [official documentation](https://knuckles-team.github.io/craft-suite-api/).

---

## Overview

The MCP connector for the ArtCraft suite. It serves **every operation of the
ArtCraft backend API as one typed tool** (268 today), generated from the
backend's published API description, and the suite's desktop apps as lazily
loaded MCP upstreams (see [the apps spec](specs/craft-suite-apps/spec.md)).

---

## Backend tools

Each backend operation is the tool `craft_suite_<operationId>`, for example
`craft_suite_list_tags_handler`, `craft_suite_omni_gen_image_models_handler`,
`craft_suite_omni_api_image_generate_handler` or
`craft_suite_omni_upload_image_media_file_handler`. Inputs and outputs are typed
from the description. Reads (GET) are annotated read-only.

| Class | Operations | Policy |
| --- | --- | --- |
| read | 92 | Runs directly |
| generation | 62 | Write: operator switch plus confirmation |
| upload | 24 | Write; the file part is base64 text, sent as a binary multipart part |
| account | 21 | Write (sessions, keys, credentials, profile) |
| moderation | 10 | Write |
| write | 59 | Write (folders, tags, bookmarks, ratings and other changes) |

Every refusal is a typed result `{cancelled, operation, reason, write_class}`:
`BACKEND_NOT_CONFIGURED` with no base URL, `WRITES_DISABLED` without the operator
switch, or the SDK confirmation refusal. Every write decision is logged to the
`craft_suite_api.audit` logger.

---

## Package identity

The connector is `craft-suite-api`, imported as `craft_suite_api`, with the
`craft-suite-mcp` command and `CRAFT_SUITE_API_` configuration prefix.

---

## Usage

| Setting | Meaning |
| --- | --- |
| `CRAFT_SUITE_API_BASE_URL` | The backend HTTPS origin, without a path. Unset: every backend call refuses. |
| `CRAFT_SUITE_API_TOKEN_REF` | An SDK credential reference (for example `env://CRAFT_SUITE_SESSION`) sent as the `session` header. |
| `CRAFT_SUITE_API_ALLOW_WRITES` | Default false. Enables writes; each one still needs confirmation (elicited, or `confirm=true`). |
| `CRAFT_SUITE_API_ALLOW_PLAINTEXT` | Default false. Allows a credential over plain HTTP. |

TLS verification stays on. Redirects are not followed, each request is tried
once with a 30 s timeout, and responses are capped at 16 MiB. Graph ingestion is
unavailable.

```json
{"name":"craft_suite_omni_gen_image_models_handler","arguments":{}}
```

---

## Provenance

`craft_suite_api/api_spec/backend.openapi.json` is the backend's published API
description, kept byte for byte and pinned by sha256 in
`craft_suite_api/api_spec/backend.source.json`. Both ship in the package. When
the server first builds the backend tools, `craft_suite_api/backend_spec.py`
checks the pin and repairs the document's known defects in memory (missing
references, untyped parameters, multipart upload bodies, the session scheme).
Nothing generated is committed and there is no regenerate step. The backend
source is under its own source-available licence: only the interface
description is used. To take a new description, replace the pinned file,
update the sha256 and run `python -m pytest tests -q`.

---

## Validation boundary

Tests use the real SDK HTTP, auth and MCP components with a fake transport at
the backend boundary. Writes are proven there; live writes need the operator
switch and a backend credential.

---

## Installation

```bash
uv pip install "craft-suite-api[mcp]"
uv pip install "craft-suite-api[all]"
```

---

## Documentation

The complete documentation is published as the
[official documentation site](https://knuckles-team.github.io/craft-suite-api/) and is
the recommended reference for installation, deployment, and day-to-day operation.

---

## Repository Owners

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=example&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/example)
![GitHub User's stars](https://img.shields.io/github/stars/example)

---

## Contribute

Contributions are welcome! Please ensure code quality by running local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Run test suites using `pytest`
