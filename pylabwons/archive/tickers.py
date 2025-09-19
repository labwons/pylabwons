from pylabwons.typesys import classproperty
from pylabwons.util.path import ARCHIVE_LOCAL
from pylabwons.util.prep import Prep
from pylabwons.archive import exdef
from pandas import DataFrame
import pandas as pd


class Tickers:

    @classmethod
    def read(cls, name:str, date:str="") -> DataFrame:
        files = ARCHIVE_LOCAL.files.copy()
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

    def rebase(self):
        exdef.check_sectors(self.sectors)

        resource = self.basics, self.corporations, self.sectors, exdef.sectors
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
        data.to_csv(self._src_.replace('.parquet', '.csv'), encoding='euc-kr')
        return


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    tickers = Tickers()
    # tickers.rebase()
    # print(tickers)
    print(tickers.subjects)
