from pylabwons.typesys import classproperty, metaclass
from pylabwons.util.path import ARCHIVE
from pylabwons.util.tradingdate import TradingDate
from pylabwons.util.prep import Prep
from pylabwons.read import exdef
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

    # @property
    # def ones(self) -> DataFrame:
    #     filtered = filtered[~(filtered['industryCode'].isna() | filtered['sectorCode'].isna())]
    #     filtered = filtered[filtered['marketCap'] >= 5e+10]
    #     filtered = filtered[filtered['amount'] >= 2e+8]
    #     return filtered

    def rebase(self):
        exdef.check_sectors(exdef.ex_sectors, self.sectors)

        resource = self.basics, self.corporations, self.sectors, exdef.ex_sectors
        lengths = {len(df): df for df in resource}

        data = Prep.smart_concat(*resource, axis=1)
        base = lengths[max(lengths.keys())]
        data = data[data.index.isin(base.index)]

        data = data[
            (data['market'] != 'KONEX') & \
            (~data['name'].isna()) & \
            (~(data['name'].str.contains('스팩') & data['name'].str.contains('호')))
        ].copy()

        missing = data[data['industryCode'].isna() | (data['sectorCode'].isna())]
        missing = missing.sort_values(by='marketCap', ascending=False)
        if not missing.empty:
            print(f"[WARNING] There are {len(missing)} tickers with missing sector or industry codes.")
            for ticker, row in missing.iterrows():
                print(f"""{{
    "ticker": "{ticker}",
    "name": "{row['name']}",
    "sectorCode": "__sectorCode__",
    "industryCode": "__industryCode__",
    "KRXIndustry": "{row['KRXIndustry']}",
    "products": "{row['products']}",
}},""")

        data.to_parquet(self._src_, engine='pyarrow')
        data.to_csv(self._src_.replace('.parquet', '.csv'), encoding='utf-8')
        super().__init__(data)
        return


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    tickers = Tickers()
    tickers.rebase()
    print(tickers)
