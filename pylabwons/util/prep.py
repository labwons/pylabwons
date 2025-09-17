from pandas import DataFrame, Series
from typing import Union
import pandas as pd


class Prep:

    @classmethod
    def smart_concat(cls, *args:DataFrame, **kwargs) -> DataFrame:
        base = args[0].copy()
        for df in args[1:]:
            df.columns = [f'{col}_other' if col in base.columns else col for col in df.columns]
            rebase = pd.concat([base, df], **kwargs).copy()
            others = [c for c in rebase.columns if c.endswith('_other')]
            for col in others:
                key = col.replace('_other', '')
                if len(rebase[col].dropna()) != len(rebase[key].dropna()):
                    rebase[key] = rebase[key].combine_first(rebase[col])
            base = rebase.drop(columns=others)
        return base