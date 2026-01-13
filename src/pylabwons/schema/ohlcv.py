from pandas import DataFrame, Series, MultiIndex
from typing import Any, List, Union
import numpy as np
import pandas as pd


class Ohlcv:

    is_bundle = False

    def __new__(cls, ohlcv:DataFrame):
        cls.is_bundle = isinstance(ohlcv.columns, MultiIndex)
        return super().__new__(cls)

    def __call__(self, *tickers) -> DataFrame:
        if self.is_bundle:
            if len(tickers) == 1:
                return self.data[tickers[0]]
            return pd.concat({ticker: self.data[ticker] for ticker in tickers}, axis=1)
        return self.data

    def __contains__(self, ticker_or_indicator:str):
        if self.is_bundle:
            return ticker_or_indicator in np.unique(self.columns.values.tolist())
        return ticker_or_indicator in self.columns

    def __delitem__(self, col:Union[Any, int, slice, str]):
        if self.is_bundle:
            self.drop(columns=self.columns[self.columns.get_level_values(1) == col], inplace=True)
        else:
            self.drop(columns=[col], inplace=True)
        return

    def __getattr__(self, attr:str):
        try:
            return getattr(self.data, attr)
        except AttributeError:
            return super().__getattribute__(attr)

    def __getitem__(self, col:Union[Any, int, slice, str]) -> Union[DataFrame, Series]:
        if self.is_bundle:
            return self.data.xs(col, axis=1, level=1)
        return self.data[col]

    def __init__(self, data:DataFrame, name:str=''):
        self.data = data.copy()
        self.name = name
        return

    def __iter__(self):
        if self.is_bundle:
            for ticker in self.columns.get_level_values(0).unique():
                yield ticker
        else:
            for col in self.data:
                yield col

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return repr(self.data)

    def __setitem__(self, col:str, data:Union[DataFrame, Series]):
        if self.is_bundle:
            data.columns = MultiIndex.from_product([data.columns, [col]])
            self.data = pd.concat([self.data, data], axis=1).sort_index(axis=1)
        else:
            self.data[col] = data
        return

    def __str__(self):
        return str(self.data)

    def serialize(self) -> DataFrame:
        if self.is_bundle:
            objs = []
            for ticker in self:
                ohlcv = self(ticker).copy()
                ohlcv['ticker'] = ticker
                objs.append(ohlcv)
            return pd.concat(objs=objs, axis=0)
        return self.data



if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    key = 'KRW-H'
    src = r"E:\SIDEPROJ\labwons-analytic\src\analysis\archive\baseline.parquet"
    raw = pd.read_parquet(src, engine='pyarrow')
    unit = raw[key].copy()

    block = Ohlcv(raw)
    print(block)
    print(block('KRW-BTC')) # __call__
    print(block('KRW-BTC', 'KRW-H')) # __call__
    print('KRW-BTC' in block) # __contains__
    print('amount' in block) # __contains__
    print('mm' in block) # __contains__
    del block['open']; print(block) # __delitem__
    for col in block: print(col) # __iter__
    block['new'] = block['close'].rolling(window=20).mean(); print(block) # __setitem__
    print(block.serialize())