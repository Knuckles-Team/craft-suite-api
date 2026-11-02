# CONN-CRAFT-SUITE-API-APPS research: the ArtCraft suite as one MCP facade

This file records what the rows rely on. It describes capabilities of the ArtCraft system and the facade.

## Capabilities of the ArtCraft system

- The suite has fourteen installed app command-line programs. Eleven expose an `mcp` subcommand: photocraft, wordcraft, pdfcraft, solidcraft, vectorcraft, figcraft, effectcraft, filmcraft, soundcraft, deckcraft and cadcraft. Lightcraft, designcraft and gridcraft do not today.
- A live smoke on a host started photocraft (26 tools), wordcraft (17 tools) and solidcraft (21 tools). Each answered the MCP handshake with protocol version 2025-06-18. Pdfcraft exposes about 170 tools. The suite exposes more than 400.
- Each app `mcp` subcommand takes separate read and write automation roots. An omitted root denies access. A bridge option attaches the subcommand to a running desktop app on a loopback address with a control token or a token file.
- Tool names such as `execute`, `save`, `export` and `screenshot` occur in several apps.

## Findings

- A model cannot take 400 tools at once. Activation per app is required, and a gateway that needs the whole catalog loads and unloads by group.
- A destructive call asks the user a question. The facade must forward that question once and must not add a second prompt.
- A remote app needs an operator-supplied URL, a credential reference and a TLS profile. A desktop bridge needs a token that never appears in a command line.
- A stdio child per client session would multiply processes. The SDK pools them.

## Decisions

See "Decisions" in `plan.md`.

## Open items

None.
