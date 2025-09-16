from pandas import DataFrame, Series
from typing import Union
import pandas as pd


def smart_join(*args:DataFrame, **kwargs) -> DataFrame:
    base = args[0]
    for df in args[1:]:
        cols = [c for c in df.columns if not c in base.columns]
        base = base.join(df[cols], how='left')
    return base