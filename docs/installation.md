# Installation

This private repository currently provides source. No ArtCraft connector PyPI
release or prebuilt image has been verified. A passing source test does not
establish package availability, image startup, or a live deployment.

## Source environment

Use Python 3.12–3.14 and an approved environment with the declared SDK and package
dependencies available. The recorded validation used pinned SDK source; registry
resolution of the declared dependency closure remains unverified.

```bash
git clone https://github.com/Knuckles-Team/artcraft-api.git
cd artcraft-api
python -m pip install -e ".[mcp,test]"
```

The installation command requires repository access and a configured source for
all declared dependencies. It has not been accepted as a clean registry install.
Configure the approved provider origin, credential references and TLS policy as
described in [Usage](usage.md). Public model catalogs need no session credential.

## Local-source container recipe

The Dockerfile installs this checkout, including the generated OpenAPI contract,
through the local `.[mcp]` package target. It does not fetch an `artcraft-api`
release from an index. From the repository root on an approved image-build host:

```bash
docker build --file docker/Dockerfile --target mcp -t artcraft-api:mcp-local .
```

This recipe remains unbuilt and untested. It still resolves dependencies from the
configured index, so a source commit alone does not freeze the dependency closure.
Use the [reviewed-commit build instructions](deployment.md) before qualification;
no image digest or deployment acceptance is supplied by this repository.
