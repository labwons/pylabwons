from pandas import DataFrame, Series, MultiIndex
from typing import List, Union
import pandas as pd


class ohlcvBundle:

    def __call__(self, *tickers):
        if len(tickers) == 1:
            return self.ticker(tickers[0])
        return pd.concat({ticker: self.ticker(ticker) for ticker in tickers}, axis=1)

    def __contains__(self, column:str):
        return column in self.data[self.tickers[0]].columns

    def __delitem__(self, column:str):
        mask = self.data.columns.get_level_values(1) == column
        self.data = self.data.drop(columns=self.data.columns[mask])
        return

    def __getitem__(self, column:str):
        return self.data.xs(column, axis=1, level=1)

    def __init__(self, data:DataFrame):
        self.data = data.copy()
        return

    def __iter__(self):
        for ticker in self.tickers:
            yield self(ticker)

    def __repr__(self):
        return repr(self.data)

    def __setitem__(self, column:str, data:Union[DataFrame, Series]):
        data.columns = MultiIndex.from_product([data.columns, [column]])
        self.data = pd.concat([self.data, data], axis=1).sort_index(axis=1)
        return

    def __str__(self):
        return str(self.data)

    def _repr_html_(self):
        return getattr(self.data, '_repr_html_')()

    @property
    def stack(self) -> DataFrame:
        objs = []
        for ticker in self.tickers:
            df = self(ticker)
            df['ticker'] = ticker
            objs.append(df)
        return pd.concat(objs=objs, axis=0)

    @property
    def tickers(self) -> List[str]:
        return self.data.columns.get_level_values(0).unique().tolist()

    def ticker(self, ticker:str) -> DataFrame:
        data = self.data[ticker].copy()
        return data


class ohlcv(DataFrame):

    def __call__(self, *args, **kwargs):
        return self
