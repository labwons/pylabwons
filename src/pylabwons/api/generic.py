from functools import cached_property
from pandas import DataFrame, Series
from pylabwons.core import FnGuide, krx
from pylabwons.utils import TradingDate
import pandas as pd


class Ticker(FnGuide):

    def __init__(self, ticker:str):
        super().__init__(ticker)
        self.trading_date = TradingDate()
        self.freq = 'd'
        self.period = 10 # UNIT: YEARS
        return

    def __getitem__(self, item):
        return self.snapshot[item]

    def __repr__(self):
        return repr(self.snapshot)

    def __str__(self) -> str:
        return str(self.snapshot)
    
    def _repr_html_(self):
        return getattr(self.snapshot.to_frame(), '._repr_html_')()

    @property
    def ohlcv(self) -> DataFrame:
        kwargs = dict(
            fromdate=self.trading_date - 365 * self.period,
            todate=self.trading_date.latest,
            ticker=self.ticker,
            freq=self.freq
        )
        _key = '_'.join(kwargs.values())
        if not hasattr(self, _key):
            self.__setattr__(_key, krx.get_ohlcv(**kwargs))
        return self.__getattribute__(_key)

    @property
    def annual_market_cap(self) -> Series:
        cap = self.quarterly_market_cap
        cap = cap[cap.index.str.endswith('12') | (cap.index == cap.index[-1])]
        cap.index.name = "year"
        return cap

    @property
    def quarterly_market_cap(self) -> Series:
        kwargs = dict(
            fromdate=self.trading_date - 365 * self.period,
            todate=self.trading_date.latest,
            ticker=self.ticker,
            freq='m'
        )
        _key = '_'.join(kwargs.values())
        if not hasattr(self, _key):
            market_cap = krx.get_market_cap(**kwargs)
            market_cap = market_cap[
                market_cap.index.astype(str).str.contains('03') | \
                market_cap.index.astype(str).str.contains('06') | \
                market_cap.index.astype(str).str.contains('09') | \
                market_cap.index.astype(str).str.contains('12') | \
                (market_cap.index == market_cap.index[-1])
            ]
            market_cap.index = market_cap.index.strftime("%Y/%m")
            market_cap.index.name = "quarter"
            self.__setattr__(_key, Series(index=market_cap.index, data=market_cap['시가총액'] / 1e+8, dtype=int))
        return self.__getattribute__(_key)

    @cached_property
    def revenue_name(self) -> str:
        return self.annual_statement.columns[0]

    @cached_property
    def snapshot(self) -> Series:
        if not 'baseline' in globals():
            globals()['baseline'] = pd.read_parquet(
                'https://github.com/labwons/labwons-manager/raw/refs/heads/main/data/src/baseline.parquet',
                engine='pyarrow'
            )
        return globals()['baseline'].loc[self.ticker]