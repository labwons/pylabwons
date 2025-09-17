from pylabwons.typesys import classproperty, metaclass
from pylabwons.util.path import ARCHIVE
from pylabwons.util.tradingdate import TradingDate
from pylabwons.util.prep import Prep
from pandas import DataFrame
import pandas as pd
import os


class Tickers(DataFrame, metaclass=metaclass):

    _str_ = _src_ = os.path.join(ARCHIVE.tickers, 'tickers.parquet')

    def __init__(self):
        super().__init__(pd.read_parquet(self._src_, engine='pyarrow'))
        return

    @classmethod
    def read(cls, name:str, date:str="") -> DataFrame:
        files = ARCHIVE.files.copy()
        files = files[files['name'] == name]
        files['date'] = files['date'].astype(int)
        files = files.sort_values(by=['date'], ascending=False)
        if not date:
            file = files['path'].values[0]
        else:
            file = files[files['date'] <= int(date)]['path'].values[0]
        return pd.read_parquet(file, engine='pyarrow')

    @classproperty
    def corporations(cls) -> DataFrame:
        return cls.read("corporations")

    @classproperty
    def sectors(cls) -> DataFrame:
        return cls.read("sectors")

    @classproperty
    def basics(cls) -> DataFrame:
        return cls.read("marketbasic")

    @property
    def ones(self) -> DataFrame:
        filtered = self[self['market'] != 'KONEX'].copy()
        filtered = filtered[~(filtered['industryCode'].isna() | filtered['sectorCode'].isna())]
        filtered = filtered[filtered['marketCap'] >= 5e+10]
        filtered = filtered[filtered['amount'] >= 2e+8]
        return filtered

    def rebase(self):
        data = Prep.smart_concat(self.basics, self.corporations, self.sectors, axis=1)
        data = data[~data['name'].isna()]
        data = data[~(data['name'].str.contains('스팩') & data['name'].str.contains('호'))]
        data.to_parquet(self._src_, engine='pyarrow')
        super().__init__(data)
        return




if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    tickers = Tickers()
    # print(tickers)
    print(tickers.ones)