# Installation

`artcraft-api` is a standard Python package and a prebuilt container image.

## Requirements

- **Python 3.12–3.14**.
- SDK configuration containing the service origin, a credential reference and TLS profile selectors.

## From PyPI (recommended)

```bash
pip install artcraft-api
```

### Optional extras

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "artcraft-api[mcp]"` | MCP runtime + SDK graph client |
| `all` | `pip install "artcraft-api[all]"` | Everything above |

## From source

```bash
git clone https://github.com/Knuckles-Team/artcraft-api.git
cd artcraft-api
pip install -e ".[mcp]"
```

## Docker

```bash
IMAGE_REF='<registry>/artcraft-api@sha256:<digest>'
docker pull "$IMAGE_REF"
```
