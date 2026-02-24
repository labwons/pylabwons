from pylabwons.core.fetch.stock.fnguide import FnGuide
from pylabwons.core.fetch.market._base import _BaseDataFrame
from pylabwons.core.fetch.market import _schema as SCHEMA
from tqdm import auto
import pandas as pd
import time


class Fundamentals(_BaseDataFrame):

    _metadata = _BaseDataFrame._metadata + ['progress_bar']

    def __init__(self, src:str=SCHEMA.NUMBERS, **kwargs):
        super().__init__(src, **kwargs)
        self.progress_bar:bool = kwargs.get('progress_bar', True)
        return

    def fetch(self, *tickers:str):
        tic = time.perf_counter()
        if self.progress_bar:
            loop = auto.tqdm(enumerate(tickers))
        else:
            loop = enumerate(tickers)
        objs = []
        for n, ticker in loop:
            obj = FnGuide(ticker)
            if n == 0:
                self.logger(f'FETCH MARKET NUMBERS OF {obj.date}')
            try:
                objs.append(obj.numbers)
            except Exception as e:
                self.logger(f">>> Error while fetching: {ticker} / {e}")
                continue
            if n and n % 50 == 0:
                time.sleep(3)
        super().__init__(pd.concat(objs, axis=1).T)
        self.logger(f'{"." * 30} {len(self)} STOCKS / RUNTIME: {time.perf_counter() - tic:.2f}s')
        return


if __name__ == '__main__':
    numbers = Fundamentals()
    print(numbers)