from pylabwons.typesys import Path, Url
from pylabwons.util import USER
from dataclasses import dataclass
from pandas import DataFrame
from typing import Union
import pandas as pd
import os


PROJECT_PATH = os.path.dirname(__file__)[:os.path.dirname(__file__).rindex('pylabwons') - len(os.sep)]
ARCHIVE_PATH = os.path.join(os.path.dirname(PROJECT_PATH), 'labwons-archive')
DEFAULT_PATH = ARCHIVE_PATH
ACTIONS_PATH = os.path.join(os.getcwd(), 'labwons-archive')


@dataclass
class ARCHIVE_PATH:
    ROOT: str = os.path.dirname(__file__)[:os.path.dirname(__file__).rindex('pylabwons') - len(os.sep)]
    LOCAL: str = os.path.join(os.path.dirname(ROOT), 'labwons-archive')
    GITHUB: str = r'https://github.com/labwons/labwons-archive/raw/refs/heads/main'
    GITHUB_ACTION: str = os.path.join(os.getcwd(), 'labwons-archive')
    if os.path.exists(LOCAL):
        COLAB = AUTO_DETECT = LOCAL
    else:
        COLAB = AUTO_DETECT = GITHUB


class Archive:

    SRC = ARCHIVE_PATH
    __root__: Union[Path, Url, str, None] = None
    __meta__: DataFrame = DataFrame()

    def __new__(cls, root:str):
        if root.startswith('http'):
            cls.__root__ = __root__ = Url(root)
        else:
            cls.__root__ = __root__ = Path(root)
        cls.__meta__ = pd.read_parquet(__root__['metadata.parquet'], engine='pyarrow')
        cls.__meta__['date'] = cls.__meta__['date'].astype(int)
        return super().__new__(cls)

    def __init__(self, root:str):
        self._root = root
        return

    def __iter__(self):
        for ticker in self[self['type'] == 'ohlcv']['name']:
            yield ticker

    def __call__(self, name:str, **kwargs) -> DataFrame:
        return self.read(name, **kwargs)

    def __contains__(self, name:str) -> bool:
        return name in self.__meta__['name']

    def __getitem__(self, item):
        return self.__meta__[item]

    def __str__(self):
        return str(self.__meta__)

    @property
    def metadata(self) -> DataFrame:
        return self.__meta__

    @metadata.setter
    def metadata(self, metadata:DataFrame):
        self.__meta__ = metadata

    @property
    def path(self) -> Union[Path, Url]:
        return self.__root__

    def read(self, name:str, **kwargs) -> DataFrame:
        meta = self[self['name'] == name]
        if meta.empty:
            raise AttributeError(f'{name} NOT FOUND IN ARCHIVE')
        if len(meta) > 1:
            for key, val in kwargs.items():
                meta = meta[meta[key] == val]
        if len(meta) > 1:
            meta = meta[meta['date'] == meta['date'].max()]
        if len(meta) > 1:
            meta = meta[meta['extension'] == 'parquet']
        if len(meta) > 1:
            meta = meta.iloc[[0]]
        meta = meta.iloc[0]
        if meta.empty:
            return DataFrame()
        return getattr(pd, f'read_{meta.extension}')(f'{self._root}/{meta.path}')


# Alias
ROOT = ARCHIVE_PATH


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    archive = Archive(ARCHIVE_PATH.GITHUB)
    # print(archive)
    # print(archive.read('tickers'))
    # print(archive('tickers'))
