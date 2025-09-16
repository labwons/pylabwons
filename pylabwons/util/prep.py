from pandas import DataFrame, Series
from typing import Union
import pandas as pd


def smart_merge(*args:DataFrame, **kwargs) -> DataFrame:
    base = args[0]
    base.index.name = 'ticker'
    base.reset_index(inplace=True)
    for df in args[1:]:
        df.index.name = 'ticker'
        df.reset_index(inplace=True)
        rebase = base.merge(df, on='ticker', suffixes=('', '_merge'))

        for col in base.columns:
            if col in df.columns:
                rebase[col] = rebase[col].combine_first(rebase[f'{col}_merge'])
                rebase.drop(columns=[f'{col}_merge'], inplace=True)
        base = rebase
    return base.set_index(keys='ticker')