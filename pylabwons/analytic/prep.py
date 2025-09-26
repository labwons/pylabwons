from pandas import DataFrame, Series
from typing import Union
import pandas as pd



def smart_concat(*args:DataFrame, **kwargs) -> DataFrame:
    """
    데이터프레임 병합
    입력 데이터프레임 중 인덱스 기준은 첫번째 데이터프레임으로 하며 열은 후순위 데이터프레임 값을 우선으로 함
    :param args:
    :param kwargs:
    :return:
    """
    base = args[0].copy()
    for df in args[1:]:
        df.columns = [f'{col}_other' if col in base.columns else col for col in df.columns]
        rebase = pd.concat([base, df], **kwargs)
        rebase = rebase[rebase.index.isin(base.index)].copy()

        others = [c for c in rebase.columns if c.endswith('_other')]
        for col in others:
            key = col.replace('_other', '')
            if len(rebase[col].dropna()) != len(rebase[key].dropna()):
                rebase[key] = rebase[col].combine_first(rebase[key])
        base = rebase.drop(columns=others)
    return base