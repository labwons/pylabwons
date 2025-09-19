from pylabwons.read.addr import ARCHIVE
from pandas import DataFrame
import pandas as pd


class Tickers(DataFrame):

    _src_ = ARCHIVE.tickers

    def __init__(self):
        super().__init__(pd.read_parquet(self._src_, engine='pyarrow'))
        return

    @property
    def subjects(self) -> DataFrame:
        filtered = self.copy()
        filtered = filtered[
            (filtered['open'] != 0) & \
            (filtered['amount'] >= 5e+8)
        ]
        return filtered


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    tickers = Tickers()
    # tickers.rebase()
    # print(tickers)
    print(tickers.subjects)
