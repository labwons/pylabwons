__all__ = [
    "Archiving",
    "classproperty",
    "DataDictionary",
    "Fetch",
    "Logger",
    "metaclass",
    "Prep",
    "Tickers",
    "TradingDate",

    "USER"
]

from .typesys import (
    metaclass,
    classproperty,
    DataDictionary
)

from .util.logger import Logger
from .util.tradingdate import TradingDate
from .util.prep import Prep

from . import archiving as Archiving
from . import fetch as Fetch

from .access.tickers import Tickers


class USER:
    from os import environ

    ACTION = environ.get("GITHUB_EVENT_NAME", None)
    if any("COLAB" in e for e in environ):
        HOST = "COLAB"
    elif ACTION is None:
        HOST = "LOCAL"
    else:
        HOST = "GITHUB"

    ENV = environ.get("USERDOMAIN", None)
