from .series import get_ohlcv, get_foreign_rates
from pandas import DataFrame


class Stock:

    def __init__(self, ticker:str, **kwargs):
        self.ticker = ticker
        self.kwargs = kwargs
        return

    def __setattr__(self, key: str, value):
        self.kwargs[key] = value

    @property
    def ohlcv(self) -> DataFrame:
        return get_ohlcv(self.ticker, **self.kwargs)

    @property
    def foreignRates(self) -> DataFrame:
        return get_foreign_rates(self.ticker, **self.kwargs)

