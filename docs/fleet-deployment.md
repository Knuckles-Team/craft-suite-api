# Fleet deployment behind arbora

The facade registers once with the arbora gateway; no app gets its own fleet
entry (CONN-CRAFT-SUITE-API-APPS-R008). The gateway treats the server as one
catalog named `craft-suite-api`.

## Settings

```bash
# Every namespace active on startup: the gateway catalog holds all apps.
SCION_UPSTREAM_ACTIVATION=active
# The operator overlay, when a deployment swaps an app to http or bridge.
SCION_UPSTREAMS_FILE=/etc/craft-suite/upstreams.toml
```

The connector's existing `connectors` entry in the org manifest is what the
gateway coverage gate (`ARBORA-FLEET-R060`) counts; the facade adds no
additional manifest entries.

## Loading one app at a time

Every proxied tool carries the metadata key `scion/upstream` with the value
`{"namespace": "<app>", "upstream": "<app>"}`. The gateway reads the
namespace as the item group, so a whole app loads and unloads as one unit:

1. `fleet.tools.load` with `groups = ["photocraft"]` loads only
   `photocraft_*` tools into the session.
2. `fleet.tools.unload` with `groups = ["photocraft"]` removes them; other
   loaded apps (for example `wordcraft`) stay loaded.
3. An unknown group returns an empty result and no error.
4. A registered server with no admitted tool reports `UNAVAILABLE`.

The connector adds no refusal codes for this seam; the gateway's own codes
apply.

## Pins

A tool pin (`ARBORA-FLEET-R059`) names a namespaced tool id such as
`photocraft_execute`, so a pinned tool survives a gateway restart: the pin
refers to the namespace, not to a session-local handle.

## Artifact exchange

Every app runs its calls through the SDK artifact exchange. Set `SCION_EXCHANGE_FILE` to a copy of [`exchange.example.json`](exchange.example.json) with real endpoints and secret references:

- The `objects` sink keeps a durable copy in an S3-compatible object store and returns a signed URL valid for 7 days.
- The `files` sink writes to a WebDAV file share folder `ArtCraft/<app>/<YYYY-MM-DD>/<run>/`, which a desktop sync client mirrors.

Optional knobs: `SCION_EXCHANGE_STAGING_ROOT` (per-run staging directories; the apps receive its `in` and `out` trees as roots), `SCION_EXCHANGE_MAX_INPUT_BYTES`, `SCION_EXCHANGE_MAX_OUTPUT_BYTES`, `SCION_EXCHANGE_RETENTION_S` and `SCION_EXCHANGE_LINEAGE`. A caller groups calls into one run with the request metadata key `scion/run`. Inputs take `exchange://<sink>/<key>` or an `https` URL. Without `SCION_EXCHANGE_FILE` the apps behave as before.
