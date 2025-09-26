from pylabwons.archiving import manager_extern
from pylabwons.fetch import get_ohlcv
from pylabwons.util.prep import Prep
from pylabwons.typesys import Path
from pandas import DataFrame
from typing import Dict, List, Union
import pandas as pd
import numpy as np
import os


PROJECT_PATH = os.path.dirname(__file__)[:os.path.dirname(__file__).rindex('pylabwons') - len(os.sep)]
ARCHIVE_PATH = os.path.join(os.path.dirname(PROJECT_PATH), 'labwons-archive')
DEFAULT_PATH = ARCHIVE_PATH
ACTIONS_PATH = os.path.join(os.getcwd(), 'labwons-archive')


class Archive(DataFrame):

    __root__: Union[Path, str, None]=None

    def __new__(cls, root:str=""):
        if not root:
            root = ARCHIVE_PATH
        cls.__root__ = Path(root)
        return super().__new__(cls)

    @classmethod
    def build_metadata(cls) -> DataFrame:
        objs = []
        for key in os.listdir(cls.__root__):
            if key.startswith('.'):
                continue
            for _root, _, files in os.walk(os.path.join(cls.__root__, key)):
                for file in files:
                    dirs = _root.split(os.sep)
                    name, extension = file.split('.')
                    path = os.path.join(_root, file)
                    if name != key == 'tickers':
                        date = dirs[-1]
                    elif extension == 'log':
                        date = name
                    elif key == 'ohlcv':
                        date = pd.read_parquet(path, engine='pyarrow').index[-1].strftime('%Y%m%d')
                    else:
                        date = np.nan
                    objs.append({
                        'name': name,
                        'type': key,
                        'extension': extension,
                        'path': path.replace(cls.__root__, ""),
                        'date': date
                    })

        data = DataFrame(objs)
        data.loc[data['name'] == 'tickers', 'date'] = data[data['name'] == 'market']['date'].sort_values().values[-1]
        data.to_parquet(cls.__root__['metadata.parquet'], engine='pyarrow')
        data.to_csv(cls.__root__['metadata.csv'], encoding='utf-8')
        super().__init__(data)
        return data

    def __init__(self, *args, **kwargs):
        super().__init__(pd.read_parquet(self.__root__['metadata.parquet'], engine='pyarrow'))
        self['date'] = self['date'].astype(int)
        return

    def __call__(self, name:str, date:str=""):
        return self.read(name=name, date=date)

    @property
    def PATH(self) -> Path:
        return self.__root__

    def push(self, data:DataFrame, *path):
        to = self.PATH[*path]
        if to.endswith('.parquet'):
            data.to_parquet(to, engine='pyarrow')
        elif to.endswith('.csv'):
            data.to_csv(to, encoding='euc-kr')
        elif to.endswith('.pkl'):
            data.to_pickle(to)
        else:
            raise TypeError(f'File {to} not supported.')

        if path[0] == "tickers":
            data = dict(zip(('type', 'date', 'file'), tuple(path)))
            data['name'], data['extension'] = data['file'].split('.')
            data['path'] = to.replace(self.PATH, "")
            del data['file']
            meta = pd.concat([self, DataFrame([data])], axis=0, ignore_index=True)
            meta['date'] = meta['date'].astype(str)
            meta.to_parquet(self.PATH['metadata.parquet'], engine='pyarrow')
            meta.to_csv(self.PATH['metadata.csv'], encoding='utf-8')
            super().__init__(meta)
        return

    def ohlcv_backfill(self, *tickers):
        for ticker in tickers:
            ohlcv = get_ohlcv(ticker)
            ohlcv.to_parquet(self.PATH[f'ohlcv{os.sep}{ticker}.parquet'], engine='pyarrow')
        return

    def ohlcv_load_actions(self) -> Dict[str, List[str]]:
        """
        CLASSIFY OHLCV DATA: WHETHER TO UPDATE OR FETCH
        :return:
        """
        existed = self.ohlcv_tickers()
        market = self[self['name'] == 'market']
        date_gaps = market[
            (max(self[self['type'] == 'ohlcv']['date'].unique()) <= market['date']) & \
            (market['date'] <= max(market['date']))
        ]['date'].values
        last_market = self('market', date_gaps[0])
        curr_market = self('market', date_gaps[-1])
        shares = pd.concat({'last': last_market['shares'], 'curr': curr_market['shares']}, axis=1)
        deleter = shares[(shares['last'] != shares['curr']) & shares.index.isin(self.ohlcv_tickers())].index.tolist()
        if deleter:
            for ticker in deleter:
                del self.PATH['ohlcv', f'{ticker}.parquet']
            self.build_metadata()

        to_backfill = self('tickers').copy()
        to_backfill = to_backfill[to_backfill['open'] != 0]
        to_backfill = to_backfill[
            (to_backfill['amount'] >= 5e+8) | \
            (to_backfill['marketCap'] >= 1e+11)
        ]

        to_backfill = to_backfill[~to_backfill.index.isin(self.ohlcv_tickers())]
        return {
            "existed": existed,
            "deleted": deleter,
            "backfill": to_backfill.index.tolist()
        }

    def ohlcv_update(self):
        ohlcvs = self[self['type'] == 'ohlcv'].copy()
        market = self[self['name'] == 'market'].copy()

        last_date = min(ohlcvs['date'].unique())
        fill_date = pd.to_datetime(market[market['date'] > last_date]['date'].astype(str).unique())

        markets = {date: self('market', date=date.strftime("%Y%m%d")) for date in fill_date}
        for ticker in self.ohlcv_tickers():
            ohlcv = self(ticker)
            update = [ohlcv]
            for date, data in markets.items():
                if not date in ohlcv.index and ticker in data.index:
                    patch = data.loc[[ticker]][ohlcv.columns]
                    patch.index = [date]
                    update.append(patch)
            ohlcv = pd.concat(update, axis=0).sort_index()
            ohlcv.to_parquet(self.PATH['ohlcv', f'{ticker}.parquet'], engine='pyarrow')
        return

    def ohlcv_tickers(self) -> list:
        return [f.split('.')[0] for f in os.listdir(self.PATH['ohlcv'])]

    def read(self, name: str, date: str = "") -> DataFrame:
        if "." in name:
            name = name.split(".")[0]
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

        filepath = file["path"].replace("\\", os.sep)
        path = f'{self.PATH}{filepath}'
        if file['extension'] == 'csv':
            return pd.read_csv(path, encoding='euc-kr').set_index('ticker')
        elif file['extension'] == 'parquet':
            return pd.read_parquet(path, engine='pyarrow')
        elif file['extension'] == 'pkl':
            return pd.read_pickle(path)
        raise TypeError(f'File {name} not supported.')

    def rebase_tickers(self):
        resource = [self('market'), self('corporations'), self('sectors')]
        _exdef.check_sectors(resource[-1])
        resource += [_exdef.sectors]

        lengths = {len(df): df for df in resource}
        base = lengths[max(lengths.keys())]
        data = Prep.smart_concat(*resource, axis=1)
        data = data[data.index.isin(base.index)]
        data = data[
            (data['market'] != 'KONEX') & \
            (~data['name'].isna()) & \
            (~(data['name'].str.contains('스팩') & data['name'].str.contains('호')))
        ].copy()

        missing = data[data['industryCode'].isna() | (data['sectorCode'].isna())]
        missing = missing.sort_values(by='marketCap', ascending=False)
        message = ''
        if not missing.empty:
            message = f"[WARNING] There are {len(missing)} tickers with missing sector or industry codes.\n"
            for ticker, row in missing.iterrows():
                message += f"""{{
            "ticker": "{ticker}",
            "name": "{row['name']}",
            "sectorCode": "__sectorCode__",
            "industryCode": "__industryCode__",
            "KRXIndustry": "{row['KRXIndustry']}",
            "products": "{row['products']}",
        }},\n"""

        data.to_parquet(self.PATH['tickers', 'tickers.parquet'], engine='pyarrow')
        data.to_csv(self.PATH['tickers', 'tickers.csv'], encoding='euc-kr')
        return message


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    archive = Archive()
    # print(archive)
    # print(archive.access('corporations'))
    # print(archive.access('corporations', date='20250917'))
    # print(archive.ohlcv_tickers)
    # print(archive.ohlcv_load_actions())
    # archive.ohlcv_update() # ~ 10.0s
    # archive.ohlcv_update('005930')
    # archive.build_metadata() # ~ 3.0s

    # print(PROJECT_PATH)
    # print(ARCHIVE_PATH)
