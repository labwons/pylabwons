__all__ = [
    "classproperty",
    "DataDictionary",
    "DateTime",
    "Logger",
    "metaclass",

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
from .util.tradingdate import DateTime
from .util.path import (
    PROJECT_NAME,
    PROJECT_PATH,
    PROJECT_DATA
)
from .util.logger import Logger
from os import environ


GITHUB_EVENT = environ.get("GITHUB_EVENT_NAME", None)
if any("COLAB" in e for e in environ):
    HOST = "COLAB"
elif GITHUB_EVENT:
    HOST = "GITHUB"
else:
    HOST = "LOCAL"