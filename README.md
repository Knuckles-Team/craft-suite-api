# Craft Suite API connector

The MCP connector for the ArtCraft suite. It serves **every operation of the
ArtCraft backend API as one typed tool** (268 today), generated from the
backend's published API description, and the suite's desktop apps as lazily
loaded MCP upstreams (see [the apps spec](specs/craft-suite-apps/spec.md)).

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

## Package identity

The connector is `craft-suite-api`, imported as `craft_suite_api`, with the
`craft-suite-mcp` command and `CRAFT_SUITE_API_` configuration prefix.

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

## Provenance and regeneration

`api-spec/backend.openapi.json` is the backend's published API description,
kept byte for byte and pinned by sha256 in `api-spec/backend.source.json`.
`scripts/generate_backend_tools.py` repairs its known defects deterministically
(missing references, untyped parameters, multipart upload bodies, the session
scheme) and writes `craft_suite_api/backend_openapi.json`, which ships with the
package. The backend source is under its own source-available licence: only the
interface description is used. To take a new description, replace the pinned
file, update the sha256 and run:

```bash
python scripts/generate_backend_tools.py
python scripts/generate_backend_tools.py --check
python -m pytest tests -q
```

## Validation boundary

Tests use the real SDK HTTP, auth and MCP components with a fake transport at
the backend boundary. Writes are proven there; live writes need the operator
switch and a backend credential.
