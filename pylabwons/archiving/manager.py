from pylabwons.archiving import manager_extern
from pylabwons.archiving.archive import Archive
from pylabwons.analytic.prep import smart_concat
from pylabwons.fetch import get_ohlcv
from pylabwons.typesys import DataDictionary
from pandas import DataFrame
from typing import Dict, List, Union, Tuple
import pandas as pd
import numpy as np
import os


class ArchiveManager(Archive):

    FETCH = DataDictionary({
        "MARKET": ['ohlcvs', 'market_caps', 'foreigner_rates', 'multiples', 'corporations']
    })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.build_metadata()
        return False

    def __init__(self, root:str):
        super().__init__(root)
        return

    def build_metadata(self) -> DataFrame:
        objs = []
        for key in os.listdir(self.path):
            if key.startswith('.') or key == "LICENSE":
                continue
            for _root, _, files in os.walk(self.path[key]):
                for file in files:
                    name, extension = file.split('.')
                    path = os.path.join(_root, file)
                    if name != key == 'tickers':
                        date = _root.split(os.sep)[-1]
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
                        'path': path.replace(self.path, "").replace(os.sep, '/'),
                        'date': date
                    })

        data = DataFrame(objs)
        data.loc[data['name'] == 'tickers', 'date'] = data[data['name'] == 'market']['date'].sort_values().values[-1]
        data.to_parquet(self.path['metadata.parquet'], engine='pyarrow')
        data.to_csv(self.path['metadata.csv'], encoding='utf-8')
        self.metadata = data
        return data

    def push(self, data:DataFrame, *path):
        to = self.path[*path]
        if to.endswith('.parquet'):
            data.to_parquet(to, engine='pyarrow')
        elif to.endswith('.csv'):
            data.to_csv(to, encoding='euc-kr')
        elif to.endswith('.pkl'):
            data.to_pickle(to)
        else:
            raise TypeError(f'File {to} not supported.')
        return

    def ohlcv_backfill(self, *tickers):
        for ticker in tickers:
            ohlcv = get_ohlcv(ticker)
            ohlcv.to_parquet(self.path[f'ohlcv{os.sep}{ticker}.parquet'], engine='pyarrow')
        self.build_metadata()
        return

    def ohlcv_load_actions(self, baseline:DataFrame) -> Dict[str, List[str]]:
        """
        CLASSIFY OHLCV DATA: WHETHER TO UPDATE OR FETCH
        :return:
        """
        subjects = baseline[baseline['open'] != 0]
        subjects = subjects[
            (subjects['amount'] >= 5e+8) | \
            (subjects['marketCap'] >= 1000e+8)
        ]

        existing = self[self['type'] == 'ohlcv']['name'].to_list()
        deleted = []
        for ticker in existing.copy():
            if not ticker in subjects.index:
                del self.path['ohlcv', f'{ticker}.parquet']
                deleted.append(ticker)
                existing.remove(ticker)
        backfill = subjects[~subjects.index.isin(existing)].index.tolist()
        return {
            "existed": existing,
            "deleted": deleted,
            "backfill": backfill
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

    @staticmethod
    def rebase(*blocks) -> Tuple[DataFrame, DataFrame]:
        args = list(blocks) + [manager_extern.sectors]
        base = smart_concat(*args, axis=1)
        base = base[
            (base['market'] != 'KONEX') & \
            (~base['name'].isna()) & \
            (~(base['name'].str.contains('스팩') & base['name'].str.contains('호')))
        ].copy()

        missing = base[base['industryCode'].isna() | (base['sectorCode'].isna())]
        missing = missing.sort_values(by='marketCap', ascending=False)
        missing = missing[missing['marketCap'] > 1000e+8]
        return base, missing


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    from pylabwons.archiving.archive import ARCHIVE_PATH

    am = ArchiveManager(ARCHIVE_PATH.LOCAL)
    print(am.build_metadata())

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
