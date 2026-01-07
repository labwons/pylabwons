from pandas import DataFrame, MultiIndex
from pylabwons.core.detector import Detector
from pylabwons.core.viewer import TickerView
from typing import Any, Union


class BackTester(Detector, TickerView):

    def __init__(self, ohlcv: Union[Any, DataFrame]):
        if not isinstance(ohlcv, DataFrame):
            try:
                ohlcv = getattr(ohlcv, 'ohlcv')
            except AttributeError:
                raise TypeError()
        Detector.__init__(self, ohlcv)
        if not isinstance(self._inst.columns, MultiIndex):
            TickerView.__init__(self, ohlcv)
        return

    def calc_return(self, n:int):
        high = (self._inst['high'].rolling(n).max() / self._inst['close'] - 1).shift(-n)
        low = (self._inst['low'].rolling(n).min() / self._inst['close'] - 1).shift(-n)
        self[f'return{n}High'] = high
        self[f'return{n}Low'] = low
        return




