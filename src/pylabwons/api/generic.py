from pandas import DataFrame
from pylabwons.core import Detector, TickerView


class Ticker(Detector, TickerView):

    def __init__(self, ohlcv: DataFrame):
        Detector.__init__(self, ohlcv)
        TickerView.__init__(self, ohlcv)
        return