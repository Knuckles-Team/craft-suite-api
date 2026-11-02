# Gateway fleet seam contract

Provider: arbora ARBORA-FLEET-R061
Consumer: craft-suite-api CONN-CRAFT-SUITE-API-APPS-R008

Counterpart: arbora `specs/fleet-catalog-and-tools/requirements.md`, row `ARBORA-FLEET-R061`.

## Wire shape

The facade is one fleet server named `craft-suite-api`. Every proxied tool carries the metadata key `scion/upstream` with the value `{namespace, upstream}`. The gateway reads `namespace` as the item group. A deployment behind the gateway sets `SCION_UPSTREAM_ACTIVATION=active`, so the gateway catalog holds every app's tools. The gateway operations `fleet.tools.load` and `fleet.tools.unload` accept `groups`.

## Refusal codes

The connector adds no code. The gateway reports `UNAVAILABLE` for a registered server with no admitted tool (`ARBORA-FLEET-R060.4`). An unknown group returns an empty result and no error.
