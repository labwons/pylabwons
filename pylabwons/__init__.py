__all__ = [
    "classproperty",
    "DataDictionary",
    "Fetch",
    "Logger",
    "metaclass",
    "Prep",
    "Tickers",
    "TradingDate",

    "HOST",
    "GITHUB_EVENT",
    "PROJECT_NAME",
    "PROJECT_PATH",
    "PROJECT_DATA"
]

from .typesys import (
    metaclass,
    classproperty,
    DataDictionary
)

from .util.logger import Logger
from .util.path import (
    PROJECT_NAME,
    PROJECT_PATH,
    PROJECT_DATA
)
from .util.tradingdate import TradingDate

from .util.prep import Prep

from . import fetch as Fetch

from .read.tickers import Tickers

from os import environ


GITHUB_EVENT = environ.get("GITHUB_EVENT_NAME", None)
if any("COLAB" in e for e in environ):
    HOST = "COLAB"
elif GITHUB_EVENT:
    HOST = "GITHUB"
else:
    HOST = "LOCAL"