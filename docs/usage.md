# Usage and validation boundary

Every backend operation is one typed tool, `craft_suite_<operationId>`, generated
from the backend's published API description. See the
[README](https://github.com/Knuckles-Team/craft-suite-api/blob/main/README.md#backend-tools)
for the classes, settings and refusal shapes.

- Reads run directly. Pass returned cursors unchanged to page.
- Writes (generation, upload, account, moderation and other changes) need
  `CRAFT_SUITE_API_ALLOW_WRITES=true` and a confirmation. A client that can elicit
  is asked once; a client that cannot is refused with a typed result and may repeat
  the call with `confirm=true`. `confirm` is never sent to the backend.
- Upload tools take the file as base64 text in the `file` argument.
- With no `CRAFT_SUITE_API_BASE_URL`, every backend call returns
  `BACKEND_NOT_CONFIGURED`.
- Every write decision (`refused`, `unconfirmed`, `sent`) is logged to
  `craft_suite_api.audit` with the tool and write class.

Graph ingestion is unavailable. A tenant/source-scoped mapping and a complete
receipt contract need a separate review.
