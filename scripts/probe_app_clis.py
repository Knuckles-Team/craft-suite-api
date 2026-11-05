#!/usr/bin/env python
"""The ``craft-suite-probe`` console script, run from the repository root.

The implementation lives in the package (``craft_suite_api.probe``) so the
installed entry point and this wrapper share one code path.
"""

from craft_suite_api.probe import main

if __name__ == "__main__":
    raise SystemExit(main())
