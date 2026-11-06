# CONN-CRAFT-SUITE-API research: the whole backend API as typed tools

This file records what rows R007 to R009 rely on. It describes capabilities, not products.

## Capabilities of the backend

- The backend publishes one machine-readable API description (OpenAPI 3.1). The pinned copy, `api-spec/backend.openapi.json`, describes 268 operations: 92 reads (GET) and 176 writes (160 POST, 6 PUT, 10 DELETE). Every operation has a unique operation id.
- The writes are 62 generation operations, 24 uploads, 21 account and session operations, 10 moderation operations and 59 other changes, such as folders, tags, bookmarks and ratings.
- The backend publishes no MCP server of its own. Its MCP routes only create, list, refresh and revoke MCP session credentials, which makes them account operations.
- The suite's desktop apps do publish MCP servers. The connector already mounts them as lazily loaded upstreams (`CONN-CRAFT-SUITE-API-APPS-R002`).
- The licences differ. The app packages ship permissive open-source licence files (MIT and Apache-2.0). The backend's source is under its own source-available licence, which is not an OSI licence: it allows private use and modification, and it forbids reselling the software or building a competing product. The connector uses only the published interface description. It copies and runs no backend code.

## Defects in the published description

- Four `$ref` targets are missing from the document's components.
- Five path parameters carry no schema. The 24 upload operations declare a multipart form as a bogus `request` path parameter instead of a request body. The real form schemas exist in the components under names that can be derived.
- File parts are typed as arrays of bytes, which a JSON tool argument cannot carry.
- The document declares no credential scheme. The backend reads its session credential from a `session` header.
- Three operation ids, with the namespace prefix, exceed the 64-character MCP name limit.

## Findings

- The framework's OpenAPI provider builds one typed tool per operation from a description. A build-time normalizer can repair the defects above deterministically, so no tool is written by hand.
- The provider truncates long names silently. An explicit name map, with a short hash suffix for long ids, keeps the names deterministic and lets governance map a name back to its operation.
- Write governance belongs on a sub-server mounted into the connector server. Its middleware then sees backend calls only, never the app upstreams.

## Decisions

See "Decisions" in `plan.md`.

## Open items

- Live verification of the generation and upload writes needs an operator-enabled write switch and a backend credential. The rows prove them against a fake transport.
