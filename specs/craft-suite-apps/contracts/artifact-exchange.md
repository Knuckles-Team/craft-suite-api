# Artifact exchange seam contract

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R914.13
Consumer: craft-suite-api CONN-CRAFT-SUITE-API-APPS-R013

Provider spec: [SCION-CONNECTOR-CONTROL](https://github.com/Knuckles-Team/scion-sdk/blob/main/specs/scion-connector-control/requirements.md).

## Wire shape

The consumer sets `exchange=ExchangeBinding(path_args=...)` on each `UpstreamDecl`. The operator sets `SCION_EXCHANGE_FILE` to one JSON document:

```json
{
  "stores": {
    "objects": {"backend": "s3", "endpoint": "https://objects.example", "presign_endpoint": "https://objects.example",
                "credentials": {"access_key_id": "openbao://kv/exchange#access_key", "secret_access_key": "openbao://kv/exchange#secret_key"}},
    "files": {"backend": "webdav", "endpoint": "https://files.example/remote.php/dav/files/svc",
              "credentials": {"username": "env://FILES_USER", "password": "openbao://kv/exchange#files_password"}}
  },
  "sinks": [
    {"name": "objects", "store": "objects", "bucket": "artifacts", "path_template": "{namespace}/{date}/{run}/{name}", "signed_url_ttl_s": 86400, "required": true},
    {"name": "files", "store": "files", "bucket": "Exports", "path_template": "{namespace}/{date}/{run}/{name}"}
  ]
}
```

A caller may group calls into one run with the request metadata key `scion/run`. An input argument may hold `exchange://<sink>/<key>` or an `https` URL. The tool result appends one `resource_link` content block per output. The result metadata key `scion/artifacts` lists each output:

```json
{"name": "out.png", "sha256": "<hex>", "size": 1024, "media_type": "image/png",
 "locations": [{"sink": "objects", "key": "photo/2026-11-04/run1/out.png", "url": "https://objects.example/..."},
               {"sink": "files", "key": "photo/2026-11-04/run1/out.png"}]}
```

## Refusal codes

Configuration: `EXCHANGE_CONFIG_INVALID`, `EXCHANGE_TEMPLATE_INVALID`, `STORAGE_SECRET_LITERAL`, `STORAGE_CONFIG_INVALID`, `STORAGE_EGRESS_REFUSED`. Call time, before the upstream runs: `EXCHANGE_RUN_ID_INVALID`, `EXCHANGE_SINK_UNKNOWN`, `EXCHANGE_URL_INPUT_DISABLED`, `EXCHANGE_EGRESS_REFUSED`, `EXCHANGE_INPUT_TOO_LARGE`, `EXCHANGE_INPUT_FAILED`. After the upstream returns, in metadata only: `EXCHANGE_OUTPUT_TOO_LARGE`, `EXCHANGE_OUTPUT_LIMIT`, `EXCHANGE_PUBLISH_FAILED`, `EXCHANGE_LINEAGE_FAILED`. The consumer adds no code of its own for these cases.

## Authoritative types

- `ExchangeBinding` in `scion_sdk/mcp/upstreams/model.py`.
- `ExchangeSettings` and `SinkDecl` in `scion_sdk/exchange/config.py`.
- `PublishedArtifact` and `ArtifactLocation` in `scion_sdk/exchange/publish.py`.

## Test vectors

- `tests/upstreams/test_upstream_exchange.py` in scion-sdk.
- `tests/exchange/test_exchange_served.py` in scion-sdk.
