from pylabwons.archiving import _exdef
from pylabwons.fetch import get_ohlcv
from pylabwons.util.prep import Prep
from pylabwons.typesys import Path
from pandas import DataFrame
from typing import List
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
        super().__init__(pd.read_parquet(self.__root__['metadata.parquet'], engine='pyarrow'))
        self['date'] = self['date'].astype(int)
        return

    def __call__(self, name:str, date:str=""):
        return self.read(name=name, date=date)

    @property
    def PATH(self) -> Path:
        return self.__root__

    def export_metadata(self, data:DataFrame=DataFrame()):
        if data.empty:
            data = []
            for key in os.listdir(self.__root__):
                if key.startswith('.'):
                    continue

                for _root, _, files in os.walk(os.path.join(self.__root__, key)):
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
                        data.append({
                            'name': name,
                            'type': key,
                            'extension': extension,
                            'path': path.replace(self.PATH, ""),
                            'date': date
                        })

            data = DataFrame(data)
            data.loc[data['name'] == 'tickers', 'date'] = data[data['name'] == 'market']['date'].sort_values().values[-1]

        data.to_parquet(self.PATH['metadata.parquet'], engine='pyarrow')
        data.to_csv(self.PATH['metadata.csv'], encoding='utf-8')
        super().__init__(data)
        return

    def ohlcv_backfill(self, *tickers):
        for ticker in tickers:
            ohlcv = get_ohlcv(ticker)
            ohlcv.to_parquet(self.PATH[f'ohlcv{os.sep}{ticker}.parquet'], engine='pyarrow')
        return

    def ohlcv_load_actions(self) -> List[str]:
        """
        CLASSIFY OHLCV DATA: WHETHER TO UPDATE OR FETCH
        :return: List[str] BACKFILL REQUIRED TICKERS
        """
        market = self[self['name'] == 'market']
        date_gaps = market[
            (max(self[self['type'] == 'ohlcv']['date'].unique()) <= market['date']) & \
            (market['date'] <= max(market['date']))
        ]['date'].values
        last_market = self('market', date_gaps[0])
        curr_market = self('market', date_gaps[-1])
        shares = pd.concat({'last': last_market['shares'], 'curr': curr_market['shares']}, axis=1)
        diff_shares = shares[(shares['last'] != shares['curr']) & shares.index.isin(self.ohlcv_tickers())].index
        if not diff_shares.empty:
            for ticker in diff_shares:
                del self.PATH['ohlcv', f'{ticker}.parquet']
            self.export_metadata()

        to_backfill = self('tickers').copy()
        to_backfill = to_backfill[to_backfill['open'] != 0]
        to_backfill = to_backfill[
            (to_backfill['amount'] >= 5e+8) | \
            (to_backfill['marketCap'] >= 1e+11)
        ]
        to_backfill = to_backfill[~to_backfill.index.isin(self.ohlcv_tickers())]
        return to_backfill.index.tolist()

    def ohlcv_update(self, *tickers):
        if not tickers:
            tickers = self.ohlcv_tickers()

        last_date = max(self[self['type'] == 'ohlcv']['date'].unique())
        fill_date = pd.to_datetime(self[self['date'] > last_date]['date'].astype(str).unique())

        market = {date: self('market', date=date.strftime("%Y%m%d")) for date in fill_date}
        for ticker in tickers:
            ohlcv = self(ticker)
            update = [ohlcv]
            for date, data in market.items():
                if not date in ohlcv.index and ticker in data.index:
                    patch = data.loc[[ticker]][ohlcv.columns]
                    patch.index = [date]
                    update.append(patch)
            ohlcv = pd.concat(update, axis=0).sort_index()
            self.loc[(self['type'] == 'ohlcv') & (self['name'] == ticker), 'date'] \
                = int(ohlcv.index[-1].strftime("%Y%m%d"))
            ohlcv.to_parquet(self.PATH['ohlcv', f'{ticker}.parquet'], engine='pyarrow')
        self.export_metadata(self.copy())
        return

    def ohlcv_tickers(self) -> list:
        return [f.split('.')[0] for f in os.listdir(self.__root__['ohlcv'])]

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
        
        path = f'{self.PATH}{file["path"]}'
        if file['extension'] == 'csv':
            return pd.read_csv(path, encoding='euc-kr').set_index('ticker')
        elif file['extension'] == 'parquet':
            return pd.read_parquet(path, engine='pyarrow')
        elif file['extension'] == 'pkl':
            return pd.read_pickle(path, engine='pyarrow')
        raise TypeError(f'File {name} not supported.')

    def rebase_tickers(self, date:str=''):
        if not date:
            date = self[self['name'] == 'market']['date'].sort_values(ascending=False).values[0]
        resource = [self('market', date), self('corporations', date), self('sectors', date)]
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
            if self.logger:
                self.logger.warning(message)
            else:
                print(message)

        data.to_parquet(self.PATH['tickers', 'tickers.parquet'], engine='pyarrow')
        data.to_csv(self.PATH['tickers', 'tickers.csv'], encoding='euc-kr')
        self.loc[self['name'] == 'tickers', 'date'] = int(date)
        return


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    archive = Archive()
    # print(archive)
    # print(archive.read('corporations'))
    # print(archive.read('corporations', date='20250917'))
    # print(archive.ohlcv_tickers)
    # print(archive.ohlcv_load_actions())
    # archive.ohlcv_update() # ~ 10.0s
    # archive.ohlcv_update('005930')
    archive.export_metadata() # ~ 3.0s



    # print(PROJECT_PATH)
    # print(ARCHIVE_PATH)
