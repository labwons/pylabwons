from pandas import DataFrame, MultiIndex
from pylabwons.core import Detector, TickerView


class Ticker(Detector):

    def __init__(self, ohlcv: DataFrame):
        super().__init__(ohlcv)
        if not self.is_bundle:
            self.viewer = TickerView(ohlcv)
        self.viewer.ohlcv = self.data
        return