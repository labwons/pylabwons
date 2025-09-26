from pylabwons.archiving.archive import Archive, ROOT
from pandas import DataFrame
from typing import Union


ARCHIVE:Archive   = Archive(ROOT.GITHUB)
TICKERS:DataFrame = ARCHIVE('tickers').copy()

class Ticker:

    def __init__(self, ticker:str):
        self.__valid__ = __valid__ = ticker in TICKERS.index
        if __valid__:
            self.basic = TICKERS.loc[ticker]
            self.ohlcv = ohlcv = ARCHIVE(ticker)
            self.__valid__ = not ohlcv.empty
        return

    def __bool__(self) -> bool:
        return self.__valid__

    def __str__(self) -> str:
        if self.__valid__:
            return str(self.basic)
        return super().__str__()

    @property
    def valid(self) -> bool:
        return bool(self)

#
# class











if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    obj = Ticker('005930')
    print(obj == True)
    print(obj.valid)
    print(obj)