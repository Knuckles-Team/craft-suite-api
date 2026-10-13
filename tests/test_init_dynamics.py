import importlib

import pytest


@pytest.mark.concept("CRAFT-001")
def test_package_imports():
    """Top-level package exposes its public API. CONCEPT:CRAFT-001"""
    module = importlib.import_module("craft_suite_api")
    assert hasattr(module, "__all__")


def test_required_import_failure_is_not_hidden(monkeypatch):
    package = importlib.import_module("craft_suite_api")
    import_module = importlib.import_module

    def unavailable_core(name):
        if name == "craft_suite_api.api":
            raise ImportError("core dependency unavailable")
        return import_module(name)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(importlib, "import_module", unavailable_core)
            with pytest.raises(ImportError, match="core dependency unavailable"):
                importlib.reload(package)
    finally:
        importlib.reload(package)
