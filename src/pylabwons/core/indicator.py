from pylabwons.schema import ohlcv, ohlcvBundle
from pandas import DataFrame, MultiIndex, Series
from typing import Any, Union


class Indicator:

    def __call__(self, *tickers):
        return self._inst(*tickers)

    def __contains__(self, column:str):
        return column in self._inst

    def __delitem__(self, column:str):
        del self._inst[column]
        return

    def __getitem__(self, column:Union[Any, str]):
        return self._inst[column]

    def __init__(self, data:DataFrame, name:str=''):
        self._data = data.copy()
        if isinstance(data.columns, MultiIndex):
            self._is_bundle = True
            self._inst = ohlcvBundle(data)
        else:
            self._is_bundle = False
            self._inst = ohlcv(data.copy())
        return

    def __repr__(self):
        return repr(self._inst)

    def __setitem__(self, column:str, data:Union[DataFrame, Series]):
        self._inst[column] = data
        return

    def __str__(self):
        return str(self._inst)

    def _repr_html_(self):
        return getattr(self._inst, '_repr_html_')()

    def add_bollinger_band(
            self,
            basis:str='tp',
            window:int=20,
            std:float=2,
    ):
        if not basis in self:
            basis = 'close'

        dev = self[basis].rolling(window=window).std()
        middle = self[basis].rolling(window=window).mean()
        upper = middle + std * dev
        lower = middle - std * dev
        width = 100 * ((upper - lower) / middle)
        upper_trend = middle + (std / 2) * dev
        lower_trend = middle - (std / 2) * dev
        self['bb_middle'] = middle
        self['bb_upper'] = upper
        self['bb_lower'] = lower
        self['bb_width'] = width
        self['bb_upper_trend'] = upper_trend
        self['bb_lower_trend'] = lower_trend
        return

    def add_drawdown(
            self,
            basis: str = 'tp',
            window: int = 20,
    ):
        if not basis in self:
            basis = 'close'
        drawdown_max = self[basis].rolling(window=window).max()
        drawdown = (self[basis] / drawdown_max) - 1
        self['dd'] = drawdown
        return

    def add_ma(
            self,
            basis: str = 'tp',
            window: int = 20,
    ):
        if not basis in self:
            basis = 'close'
        ma = self[basis].rolling(window=window).mean()
        self[f'ma{window}'] = ma
        return

    def add_macd(
            self,
            basis:str='tp',
            window_slow:int=26,
            window_fast:int=12,
            window_sign:int=9,
    ):
        __ema__ = lambda _df, _window: _df.ewm(span=_window).mean()

        if not basis in self:
            basis = 'close'

        macd = __ema__(self[basis], window_fast) - __ema__(self[basis], window_slow)
        macd_sig = __ema__(macd, window_sign)
        macd_diff = macd - macd_sig
        self['macd'] = macd
        self['macd_signal'] = macd_sig
        self['macd_diff'] = macd_diff
        return

    def add_typical_price(self):
        self['tp'] = (self['high'] + self['low'] + self['close']) / 3
        return