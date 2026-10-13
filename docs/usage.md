# Usage and validation boundary

The current backend connector has four tools and nine source-reviewed actions.
See [README](https://github.com/Knuckles-Team/craft-suite-api/blob/main/README.md#supported-operations) for the exact allowlist and
configuration. All operation inputs and outputs are generated from the reviewed
subset in `api-spec/artcraft.reviewed.openapi.json`.

Four anonymous model-catalog GETs and the service-status GET form the public read-only surface. Call `misc_operations` with `{"action":"status_alert_handler"}` to retrieve the alert and its 60000 ms refresh interval; `maybe_alert` is null when no alert is configured. Tag and folder
GETs can populate Redis session caches and therefore require explicit write
enablement plus native MCP confirmation. This is a conservative effect gate,
not a claim that they alter user-owned tags or folders. Owner checks remain at
the provider. Job keepalive polling and every generation/upload/admin route are
withheld. Do not use production credentials or guess unsupported operation IDs.

The public documentation export is not commit-attested. Exact route, handler,
response-type and 26 struct-field checks use the pinned source; enum/serializer
facet parity and actual deployment compatibility remain unverified. The video
catalog is withheld after detected schema drift; two optional folder properties
are explicitly derived from the pinned Rust declarations.

No live service tests or ingestion acceptance receipts are claimed. Graph ingestion is unavailable. A tenant/source-scoped mapping and complete receipt contract require a separate ArtCraft semantic review.

Tag/folder list `limit` inputs are optional unsigned 32-bit integers (0 through 4294967295); overflow is rejected locally. The provider still applies its 1000-row page clamp.

Native confirmation is validated with legacy negotiation and protocol 2026-07-28.
Modern requests remain pending without provider dispatch until an explicit true
acceptance returns with the same action, arguments and request state. Declines,
cancellations, missing responses and changed arguments/state are denied. Operator
write enablement remains necessary. Public catalog reads do not request confirmation.

URI and date-time formats are validated on API and MCP paths. Malformed values
are rejected without echoing the input; a missing required format checker fails
explicitly instead of silently accepting data.
