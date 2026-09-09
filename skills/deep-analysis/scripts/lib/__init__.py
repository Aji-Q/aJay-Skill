"""Shared library for ajay fetcher scripts."""
from .cache import cached, write_task_output, read_task_output, require_task_output
from .market_router import parse_ticker, is_chinese_name, TickerInfo
from . import seat_db, investor_db


def __getattr__(name):
    # Spawned pure scheduler workers should not bootstrap market SDKs. Preserve
    # lib.data_sources / from lib import data_sources on first explicit access.
    if name == "data_sources":
        from importlib import import_module
        module = import_module(f"{__name__}.data_sources")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))

__all__ = [
    "cached",
    "write_task_output",
    "read_task_output",
    "require_task_output",
    "parse_ticker",
    "is_chinese_name",
    "TickerInfo",
    "data_sources",
    "seat_db",
    "investor_db",
]
