from pylabwons.util.logger import Logger
from pylabwons.util.prep import Prep
from pylabwons.archiving import _exdef
from pylabwons.archiving.archive import Archive
from pandas import DataFrame
import pandas as pd


class ArchivePrep:

    def __init__(self, archive:Archive, logger:Logger=None):
        self.archive = archive
        self.logger = logger
        return

    def __getitem__(self, item):
        return self.archive.read(item)

    def rebase(self) -> DataFrame:
        resource = [self['basics'], self['corporations'], self['sectors']]
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
        return data


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    tickers = Tickers()
    # tickers.rebase()
    # print(tickers)
    print(tickers.subjects)
