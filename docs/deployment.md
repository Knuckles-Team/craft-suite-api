# Deployment

This page covers running `craft-suite-api` as long-lived servers.

## Build from a reviewed source commit

The production Dockerfile installs the local package and its MCP runtime extra.
No prebuilt ArtCraft connector image is currently verified. Build only on an
approved image-build host, using the exact reviewed checkout as the context:

```bash
SOURCE_COMMIT=$(git rev-parse --verify 'HEAD^{commit}')
git archive --format=tar "$SOURCE_COMMIT" | docker build \
  --file docker/Dockerfile --target mcp \
  --label "org.opencontainers.image.revision=$SOURCE_COMMIT" \
  --tag craft-suite-api:mcp-local -
```

A source commit does not freeze the index-resolved dependency closure. The shared
[runtime artifact contract](https://github.com/Knuckles-Team/pipelines/blob/7b3d18d72b5622d455ece3bbe45a9482bc6e8b5e/reference/container-runtime.md)
defines separate artifact qualification. This source correction does not build,
publish, qualify or deploy an image. Transport examples below require a separately
approved and verified environment.

> `craft-suite-api` ships an **MCP server** (console script `craft-suite-mcp`).

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`craft-suite-api` exposes its MCP server (console script `craft-suite-mcp`) four ways. Pick the
row that matches where the server runs relative to your MCP client, then copy the
matching `mcp_config.json` below.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container | `stdio` | reviewed Docker / Podman image on this host | `command` |
| 4 | Remote URL | `streamable-http` | operator-owned authenticated TLS ingress | `url` |

### 1. stdio (local subprocess)

```json
{
  "mcpServers": {
    "craft-suite-mcp": {
      "command": "craft-suite-mcp",
      "args": [],
      "env": {
        "SYSTEMTOOL": "true"
      }
    }
  }
}
```

### 2. Streamable-HTTP (local process)

```bash
craft-suite-mcp --transport streamable-http --host 127.0.0.1 --port 8000
curl -s http://loopback.invalid:8000/health        # {"status":"OK"}
```

Connect to the running process by URL:

```json
{
  "mcpServers": {
    "craft-suite-mcp": { "url": "http://loopback.invalid:8000/mcp" }
  }
}
```

### 3. Local container

Launch a container directly from `mcp_config.json` (swap `docker` for `podman` for a
daemonless runtime):

```json
{
  "mcpServers": {
    "craft-suite-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges", "--pids-limit=256",
        "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=64m",
        "-e", "TRANSPORT=stdio",
        "<registry>/craft-suite-api@sha256:<digest>"
      ]
    }
  }
}
```

Supply the provider profile through the operator-owned connector configuration mount or secret
projection. The image and this document contain no endpoint, credential, or trust material.

### 4. Remote URL (authenticated TLS ingress)

When the server is deployed remotely, connect through its operator-supplied
authenticated HTTPS ingress; no local process or image is required:

```json
{
  "mcpServers": {
    "craft-suite-mcp": { "url": "https://service.example.invalid/mcp" }
  }
}
```

Configure outbound MCP identity and trust references in SDK configuration. The server
must use direct TLS or an explicitly trusted TLS-terminating ingress and an exact
`MCP_ALLOWED_HOSTS` policy; do not commit the endpoint, credentials, or trust paths.
<!-- END GENERATED: deployment-options -->

## Docker Compose

```bash
docker compose -f docker/mcp.compose.yml up -d      # MCP server only
```
