from .logger import Logger
from .tradingdate import TradingDate

# Alias
TD = TradingDate

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