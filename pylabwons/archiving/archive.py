from pylabwons.typesys import Path
from pandas import DataFrame
import pandas as pd
import numpy as np
import os


PROJECT_PATH = os.path.dirname(__file__)[:os.path.dirname(__file__).rindex('pylabwons') - len(os.sep)]
ARCHIVE_PATH = os.path.join(os.path.dirname(PROJECT_PATH), 'labwons-archive')
DEFAULT_PATH = ARCHIVE_PATH


class Archive(DataFrame):

    __root__: Path=None

    def __new__(cls, root:str=""):
        if not root:
            root = ARCHIVE_PATH
        cls.__root__ = Path(root)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(self.list_up())
        return

    def __call__(self, *paths):
        return self.__root__[*paths]

    @classmethod
    def list_up(cls):
        data = []
        for key in os.listdir(cls.__root__):
            if key.startswith('.'):
                continue

            for _root, _, files in os.walk(os.path.join(cls.__root__, key)):
                for file in files:
                    dirs = _root.split(os.sep)
                    name, extension = file.split('.')
                    path = os.path.join(_root, file)
                    date = dirs[-1] if name != key == 'tickers' else np.nan
                    data.append({
                        'name': name,
                        'type': key,
                        'extension': extension,
                        'path': path,
                        'date': date
                    })
        return DataFrame(data)

    def read(self, name: str, date: str = "") -> DataFrame:
        files = self[self['name'] == name].copy()
        if files.empty:
            raise FileNotFoundError(f'No such file: {name}')

        if len(files) == 1:
            file = files.iloc[0]
        else:
            if files['date'].isna().all():
                file = files.iloc[-1]
            else:
                files['date'] = files['date'].astype(int)
                files = files.sort_values(by=['date'], ascending=False)
                if date:
                    file = files[files['date'] <= int(date)].iloc[0]
                else:
                    file = files.iloc[0]

        if file['extension'] == 'csv':
            return pd.read_csv(file['path'], encoding='euc-kr').set_index('ticker')
        elif file['extension'] == 'parquet':
            return pd.read_parquet(file['path'], engine='pyarrow')
        elif file['extension'] == 'pkl':
            return pd.read_pickle(file['path'])
        raise TypeError(f'File {name} not supported.')

    def refresh(self):
        super().__init__(self.list_up())
        return

    def write(self, *paths):
        return self.__root__[*paths]


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    archive = Archive()
    # print(archive)
    # print(archive.read('corporations'))
    # print(archive.read('corporations', date='20250917'))
    print(archive.to('logs', '20231001.log'))

    # print(PROJECT_PATH)
    # print(ARCHIVE_PATH)
