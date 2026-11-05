# Tool budget and activation

The facade serves the eleven ArtCraft app CLIs as pooled stdio children behind
one connector server. A direct client sees a small surface first and
activates an app only when it works on one (CONN-CRAFT-SUITE-API-APPS-R007).

## What the first list holds

A fresh session lists exactly thirteen tools:

| Group | Count | Names |
|---|---|---|
| Tier 1 backend reads | 9 | `craft_suite_<action>` |
| Registry | 4 | `registry_list_namespaces`, `registry_activate`, `registry_deactivate`, `registry_status` |

No app process starts for a direct client: every namespace is `lazy` and
inactive until it is activated.

## Why activation is per app

The suite carries about four hundred tools across the eleven apps; the
largest app exposes about 180. Listing all of them up front would crowd out
the Tier 1 surface and every model context. Activation reveals one app at a
time, and the SDK knob `max_active_namespaces` (starting value 4) caps how
many stay revealed at once.

| App | Tool count |
|---|---|
| photocraft | 26 |
| wordcraft | 17 |
| pdfcraft | 183 |
| solidcraft | 21 |
| vectorcraft | 33 |
| figcraft | 19 |
| effectcraft | 27 |
| filmcraft | 17 |
| soundcraft | 17 |
| deckcraft | 25 |
| cadcraft | 12 |

## The activation steps

1. `registry_list_namespaces` — the eleven namespaces and their states.
2. `registry_activate` with one namespace (for example `photocraft`) — the
   app starts on first use and its tools appear as `photocraft_<tool>`.
3. Work with the namespaced tools; a tool call never crosses a namespace.
4. `registry_deactivate` — the namespace hides again and its slot frees for
   the next app.
5. `registry_status` — the live state of every namespace, including error
   codes for an app that cannot start.

A deployment behind the arbora gateway sets `SCION_UPSTREAM_ACTIVATION=active`
instead; the gateway catalog then holds every app's tools and its group load
controls the exposure (see [fleet deployment](fleet-deployment.md)).
