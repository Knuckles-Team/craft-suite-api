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
