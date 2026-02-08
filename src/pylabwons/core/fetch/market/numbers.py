from pylabwons.utils.logger import Logger
from pylabwons.core.fetch.stock.fnguide import FnGuide
from functools import cached_property
from pandas import DataFrame
from typing import Dict, Iterator
import pandas as pd


class Numbers:
    logger = None

    def __new__(cls, *args, **kwargs):
        if not cls.logger:
            cls.logger = Logger(console=kwargs.get('console', False))
        return super().__new__(cls)

    def __init__(self, *tickers:str):
        self.tickers:Dict[str, FnGuide] = {ticker: FnGuide(ticker) for ticker in tickers}
        return

    def __iter__(self) -> Iterator[FnGuide]:
        for obj in self.tickers.values():
            yield obj

    @cached_property
    def overview(self) -> DataFrame:
        objs = []
        for fn in self:
            data = fn.snapshot
            data['gb'] = fn.gb
            data['reportYears'] = fn.annual_statement.index
            data['reportQuarters'] = fn.quarterly_statement.index
            objs.append(data)
        return pd.concat(objs, axis=1)