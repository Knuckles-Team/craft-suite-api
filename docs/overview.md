# craft-suite-api — Concept Overview

> **Category**: Integration | **Ecosystem Role**: MCP Server
> Built on [`scion-sdk`](https://github.com/Knuckles-Team/scion-sdk).

## Description

MCP connector for the ArtCraft suite: every operation of the ArtCraft backend
API served as one typed tool, and the suite's nineteen desktop apps served as
lazily activated MCP upstreams, each with its own content tier (skill,
ontology and per-functionality prompts).

## Architecture

- **Backend tools**: one typed tool per backend operation
  (`craft_suite_<operationId>`), generated from the backend's published API
  description; reads are annotated read-only, writes pass the operator switch
  and a confirmation.
- **App upstreams**: the nineteen app CLIs as pooled stdio children behind the
  SDK's upstream registry; a namespace activates on demand and its tools are
  served as `<namespace>_<tool>` (one app, `craft-anything`, is served under
  the hyphen-free namespace `craftanything`).
- **Command tools**: every app engine command its own tool
  (`<app>_cmd_<command>`), warmed per app at server start.
- **Content tier**: per-app ontology modules, skills and prompts packaged
  with the connector and checked for drift offline.
- **Lifecycle**: one state machine per component (backend, per app) that the
  `/ready` probe serves: warming, ready, degraded, backoff, unconfigured.

## Concept Registry

This project implements or inherits the following ecosystem concepts:

| Concept ID | Description | Source |
|:-----------|:------------|:-------|
| ECO-4.1 | MCP & Universal Skills | `scion-sdk` (inherited) |

> 📖 **Full Registry**: See [`scion-sdk/docs/overview.md`](https://github.com/Knuckles-Team/scion-sdk/blob/main/docs/overview.md) for the complete 5-Pillar concept index.
