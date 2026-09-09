"""Fresh-interpreter checks for light scheduler imports and legacy lib exports."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import textwrap


SCRIPTS = Path(__file__).resolve().parents[1]


def _fresh(code: str):
    # Import behavior must be checked before pytest's other tests load providers.
    # No provider is called; block any accidental socket connections regardless.
    preamble = """
import socket
def _no_network(*args, **kwargs):
    raise AssertionError('network is disabled in this import-only test')
socket.socket.connect = _no_network
socket.socket.connect_ex = _no_network
"""
    result = subprocess.run(
        [sys.executable, "-c", preamble + textwrap.dedent(code)],
        cwd=SCRIPTS, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_process_runner_import_does_not_load_market_sdks():
    _fresh("""
        import importlib.abc
        import sys
        class RejectProviderImport(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] in {'akshare', 'pandas', 'yfinance', 'baostock'}:
                    raise AssertionError('pure scheduler imported ' + fullname)
                return None
        sys.meta_path.insert(0, RejectProviderImport())
        from lib.pipeline.process_runner import ProcessJob, run_process_jobs
        assert callable(run_process_jobs)
        assert 'lib.data_sources' not in sys.modules
    """)


def test_dir_and_all_advertise_data_sources_without_importing_it():
    _fresh("""
        import lib
        import sys
        assert 'data_sources' in dir(lib)
        assert 'data_sources' in lib.__all__
        assert 'lib.data_sources' not in sys.modules
        assert callable(lib.cached)
        assert lib.parse_ticker('TEST').market == 'U'
        assert lib.seat_db is not None and lib.investor_db is not None
    """)


def test_explicit_data_source_imports_preserve_single_module_identity():
    _fresh("""
        import importlib
        import lib
        import sys
        assert 'lib.data_sources' not in sys.modules
        from lib import data_sources
        import lib.data_sources as direct
        assert data_sources is direct is lib.data_sources
        assert data_sources is importlib.import_module('lib.data_sources')
        assert callable(data_sources.fetch_basic)
        assert callable(data_sources.fetch_kline)
        assert lib.__dict__['data_sources'] is data_sources
    """)


def test_star_import_preserves_all_legacy_exports():
    _fresh("""
        import lib
        exported = {}
        exec('from lib import *', exported)
        assert all(name in exported for name in lib.__all__)
        assert exported['data_sources'] is lib.data_sources
        assert exported['cached'] is lib.cached
        assert exported['TickerInfo'] is lib.TickerInfo
    """)


def test_unknown_attribute_and_ordinary_submodule_import_keep_python_semantics():
    _fresh("""
        import lib
        try:
            lib.no_such_export
        except AttributeError:
            pass
        else:
            raise AssertionError('unknown attribute must raise AttributeError')
        from lib import data_integrity
        assert callable(data_integrity.validate)
    """)
