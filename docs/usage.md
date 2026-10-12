# Usage and validation boundary

The current backend connector has three tools and eight source-reviewed actions.
See [README](../README.md#supported-operations) for the exact allowlist and
configuration. All operation inputs and outputs are generated from the reviewed
subset in `api-spec/artcraft.reviewed.openapi.json`.

Four anonymous model-catalog GETs are the initial read-only surface. Tag and folder
GETs can populate Redis session caches and therefore require explicit write
enablement plus native MCP confirmation. This is a conservative effect gate,
not a claim that they alter user-owned tags or folders. Owner checks remain at
the provider. Job keepalive polling and every generation/upload/admin route are
withheld. Do not use production credentials or guess unsupported operation IDs.

The public documentation export is not commit-attested. Exact route, handler,
response-type and 24 struct-field checks use the pinned source; enum/serializer
facet parity and actual deployment compatibility remain unverified. The video
catalog is withheld after detected schema drift; two optional folder properties
are explicitly derived from the pinned Rust declarations.

No live service tests or ingestion acceptance receipts are claimed. Existing
starter ontology/ingestion examples require a separate ArtCraft semantic review.
