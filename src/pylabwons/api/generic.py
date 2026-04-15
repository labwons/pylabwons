from datetime import datetime, timedelta
from functools import cached_property
from pandas import DataFrame, Series
from pylabwons.core import FnGuide, krx
from pylabwons.utils import TradingDate
import pandas as pd


class Ticker(FnGuide):

    def __init__(self, ticker:str):
        super().__init__(ticker)
        self.trading_date = td = TradingDate()
        self.freq = 'd'
        self.period = period = 10 # UNIT: YEARS
        self.todate = todate = td.latest
        try:
            self.fromdate = td - 365 * period
        except (IndexError, KeyError, Exception):
            self.fromdate = datetime.strptime(todate, '%Y%m%d') - timedelta(365 * period)
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
            fromdate=self.fromdate,
            todate=self.todate,
            ticker=self.ticker,
            freq=self.freq
        )
        _key = '_'.join(kwargs.values())
        if not hasattr(self, _key):
            self.__setattr__(_key, krx.get_ohlcv(**kwargs))
        return self.__getattribute__(_key)

    @ohlcv.setter
    def ohlcv(self, ohlcv:DataFrame):
        times = ohlcv.index
        self.fromdate = times[0].strftime('%Y%m%d')
        self.todate = times[-1].strftime('%Y%m%d')
        diff = times.diff().days.min()
        if diff <= 2:
            self.freq = 'd'
        else:
            self.freq = 'm'
        _key = '_'.join([self.fromdate, self.todate, self.ticker, self.freq])
        self.__setattr__(_key, ohlcv)
        return

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

if __name__ == "__main__":

    stock = Ticker('000660')
    stock.ohlcv = df = pd.read_parquet(r'C:\Users\Administrator\Downloads\sample_ohlcv.parquet', engine='pyarrow')
    print(stock.ohlcv)
    print(df)
    print(df.equals(stock.ohlcv))