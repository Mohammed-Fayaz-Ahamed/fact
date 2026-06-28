from importlib.metadata import PackageNotFoundError, version

from .config import FactConfig
from .metrics import metrics

try:
    __version__ = version("fact-telemetry")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "FactConfig",
    "metrics",
    "__version__",
]