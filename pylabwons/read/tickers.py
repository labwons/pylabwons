from pylabwons.typesys import classproperty
from pylabwons.util.path import PROJECT_DATA
from pylabwons.util.tradingdate import DateTime
from pandas import DataFrame
import pandas as pd


class Tickers:

    base_date:str = DateTime.trading

    @classmethod
    def read(cls, name:str, date:str="") -> DataFrame:
        files = PROJECT_DATA.files.copy()
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
        return cls.read("corporations", cls.base_date)

    @classproperty
    def sectors(cls) -> DataFrame:
        return cls.read("sectors", cls.base_date)

    @classproperty
    def basics(cls) -> DataFrame:
        return cls.read("marketbasic", cls.base_date)



if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    print(Tickers.corporations)
    print(Tickers.sectors)
    print(Tickers.basics)