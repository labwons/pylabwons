from pylabwons.core.indicator import Indicator
from pandas import DataFrame


class Detector(Indicator):

    def detect_rapid_drop(
            self,
            basis:str='tp',
            window:int=5,
            threshold:float=0.1
    ) -> DataFrame:
        if basis == 'tp' and not basis in self:
            self.add_typical_price()

        if not 'ma20' in self:
            self.add_ma(basis=basis, window=20)

        if not 'dd' in self:
            self.add_drawdown(basis=basis, window=window)

        self['sig_rapid_drop'] = (
            (self[basis] > self['ma20']).shift(window-1) &
            (self['dd'].rolling(window=window).min() <= -threshold) &
            (self['dd'] >= -(0.8 * threshold))
            # (self['dd'] >= -(0.8 * threshold)) &
            # (self['dd'] < -(0.5 * threshold))
        )
        return self['sig_rapid_drop']