from pylabwons.utils.logger import Logger
from pylabwons.core.fetch.stock.fnguide import FnGuide
from functools import cached_property
from pandas import DataFrame
from typing import Dict, Iterator
import pandas as pd
import time


class Fundamentals(DataFrame):

    logger = None
    def __new__(cls, *args, **kwargs):
        if not cls.logger:
            cls.logger = Logger(console=kwargs.get('console', False))
        return super().__new__(cls)

    def __init__(self, src:str=''):
        if str(src).endswith('.parquet'):
            super().__init__(pd.read_parquet(src, engine='pyarrow'))
        else:
            super().__init__()
        return

    def fetch(self, *tickers:str):
        tic = time.perf_counter()
        objs = []
        for n, ticker in enumerate(tickers):
            obj = FnGuide(ticker)
            if n == 0:
                self.logger(f'FETCH MARKET NUMBERS OF {obj.date}')
            try:
                objs.append(obj.numbers)
            except Exception as e:
                self.logger(f">>> Error while fetching: {ticker} / {e}")
                continue
        super().__init__(pd.concat(objs, axis=1))
        self.logger(f'{"." * 30} {len(self)} STOCKS / RUNTIME: {time.perf_counter() - tic:.2f}s')
        return