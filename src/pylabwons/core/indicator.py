from pylabwons.schema import Ohlcv
import numpy as np
import pandas as pd


class Indicator(Ohlcv):

    def add_average_true_range(
            self,
            window:int=10,
    ):
        rng1 = self['high'] - self['low']
        rng2 = (self['high'] - self['close'].shift(1)).abs()
        rng3 = (self['low'] - self['close'].shift(1)).abs()
        if self.is_bundle:
            tr = rng1.combine(rng2, np.maximum).combine(rng3, np.maximum)
        else:
            tr = pd.concat({'rng1':rng1, 'rng2':rng2, 'rng3':rng3}, axis=1).max(axis=1)
        self['atr'] = tr.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
        return

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
        pct_b = ((self[basis] - lower) / (upper - lower)) * 2 - 1
        self['bb_middle'] = middle
        self['bb_upper'] = upper
        self['bb_lower'] = lower
        self['bb_width'] = width
        self['bb_upper_trend'] = upper_trend
        self['bb_lower_trend'] = lower_trend
        self['bb_pct_b'] = pct_b
        return

    def add_drawdown(
            self,
            basis: str = 'tp',
            window: int = 12,
    ):
        if not basis in self:
            basis = 'close'
        drawdown_max = self[basis].rolling(window=window).max()
        drawdown = (self[basis] / drawdown_max) - 1
        self['dd'] = drawdown
        return

    def add_log_return(self):
        log_return = np.log(self['close']).diff()
        self['log_return'] = log_return
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

    def add_ma_disparity(
            self,
            basis:str='tp',
            window:int=20,
    ):
        if not f'ma{window}' in self:
            self.add_ma(basis=basis, window=window)
        disparity = self[basis] / self[f'ma{window}'] * 100
        self[f'ma{window}_disparity'] = disparity
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

    def add_on_balance_volume(self):
        sign = np.sign(self['close'].diff())
        obv = (sign * self['volume']).fillna(0).cumsum()
        self['obv'] = obv
        return

    def add_obv_slope(self, window:int=12):
        if not 'obv' in self:
            self.add_on_balance_volume()

        n = window
        x_sum = n * (n - 1) / 2
        x2_sum = (n - 1) * n * (2 * n - 1) / 6
        denom = n * x2_sum - (x_sum ** 2)

        sum_y = self['obv'].rolling(window=n).sum()
        weights = np.arange(n)
        sum_xy = self['obv'].rolling(window=n).apply(lambda y: np.dot(y, weights), raw=True)
        obv_slope = (n * sum_xy - x_sum * sum_y) / denom
        self['obv_slope'] = obv_slope
        return

    def add_rsi(self, window:int=14, offset:int=0):
        delta = self['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - 100 / (1 + rs)
        if offset:
            rsi = rsi + offset
        self['rsi'] = rsi
        return

    def add_typical_price(self):
        self['tp'] = (self['high'] + self['low'] + self['close']) / 3
        return

    def add_volume_roc(
            self,
            window:int=7,
    ):
        v_ma = self['volume'].rolling(window=window).mean()
        v_roc = (self['volume'] / v_ma.shift(1))
        self["v_roc"] = v_roc
        return