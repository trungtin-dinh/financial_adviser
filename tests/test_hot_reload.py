"""A stale package left in memory by a hot deployment is fully replaced."""
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

import financial_adviser

ROOT = Path(__file__).resolve().parents[1]


def _package_modules() -> dict:
    return {name: module for name, module in sys.modules.items()
            if name == "financial_adviser" or name.startswith("financial_adviser.")}


def test_version_mismatch_reimports_every_package_module(monkeypatch):
    import financial_adviser.engine as stale_engine
    before = _package_modules()
    monkeypatch.setattr(financial_adviser, "__version__", "0.0.0-stale")
    try:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        app.run()
        assert not app.exception, app.exception
        fresh = sys.modules["financial_adviser"]
        assert fresh is not financial_adviser
        assert fresh.__version__ != "0.0.0-stale"
        import financial_adviser.engine as engine_after
        assert engine_after is not stale_engine
    finally:
        # Other tests must keep using one consistent set of classes.
        for name in _package_modules():
            del sys.modules[name]
        sys.modules.update(before)
