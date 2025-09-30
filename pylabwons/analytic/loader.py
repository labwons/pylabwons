from pylabwons.archiving.archive import Archive, ROOT
from analytic.plugin.technical import typical_price, bollinger_band, simple_ma
from pandas import DataFrame
from logging import Logger
from time import perf_counter
from typing import Any, Callable, Iterator, Union

ARCHIVE:Archive   = Archive(ROOT.AUTO_DETECT)
TICKERS:DataFrame = ARCHIVE('tickers').copy()

class Ticker:

    def __init__(self, ticker:str):
        self.__valid__ = __valid__ = ticker in TICKERS.index
        if not __valid__:
            return

        self.basic = basic = TICKERS.loc[ticker]
        self.ohlcv = ohlcv = ARCHIVE(ticker)
        self.ticker = ticker
        self.name = basic['name']

        if ohlcv.empty:
            return

        self.__ta__ = ohlcv.copy()

        # Default Plug-Ins
        self.plug(typical_price)
        self.plug(bollinger_band)
        self.plug(simple_ma)
        return

    def __bool__(self) -> bool:
        return self.__valid__

    def __getitem__(self, item) -> Union[Any, str]:
        return self.basic[item]

    def __setitem__(self, key, value):
        self.basic[key] = value

    def __str__(self) -> str:
        if self.__valid__:
            return str(self.basic)
        return super().__str__()

    @property
    def ta(self) -> DataFrame:
        return self.__ta__

    @property
    def valid(self) -> bool:
        return bool(self)

    def plug(self, plugin:Callable, *args, **kwargs):
        self.__ta__ = plugin(self.__ta__, *args, **kwargs)
        return



class Tickers:

    def __init__(self, logger:Logger=None):
        stime = perf_counter()
        self._metadata = metadata = ARCHIVE[ARCHIVE['type'] == 'ohlcv']
        self._basedata = {t: Ticker(t) for t in metadata['name']}
        self.logger = logger

        load_msg = f'LOAD {len(metadata)} ITEMS in {perf_counter() - stime:.3f}s'
        if logger:
            logger.info(load_msg)
        else:
            print(load_msg)
        return

    def __iter__(self) -> Iterator[Ticker]:
        for ticker_obj in self._basedata.values():
            yield ticker_obj

    def __getitem__(self, item) -> Ticker:
        if isinstance(item, int):
            return list(self._basedata.values())[0]
        else:
            return self._basedata[item]

    def plug(self, plugin:Callable, *args, **kwargs):
        stime = perf_counter()
        for ticker_obj in self._basedata.values():
            ticker_obj.plug(plugin, *args, **kwargs)
        plug_msg = f'PLUGGED IN SUCCESS in {perf_counter() - stime:.3f}s'
        if self.logger:
            self.logger.info(plug_msg)
        else:
            print(plug_msg)
        return


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)


    from analytic.plugin.technical import (
        backtest_return,
        bollinger_band
    )

    obj = Ticker('005930')
    obj.plug(backtest_return, 21, 42, 63, 126)
    obj.plug(bollinger_band)
    # print(obj.ohlcv)
    print(obj.ta)

    # objs = Tickers()
    # for obj in objs:
    #     print(obj.ticker, obj.name)