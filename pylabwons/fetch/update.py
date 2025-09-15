from pylabwons.util.tradingdate import DATETIME
from pylabwons.util.path import PROJECT_DATA
from pylabwons.util.logger import Logging
from pylabwons.fetch.stock import tickers
import os, time


class Tickers:

    def __init__(self, date:str='', logger:Logging=None):
        if logger and isinstance(logger, Logging):
            self.log = logger
        else:
            self.log = None

        latest_date = DATETIME.TODAY
        base_date = date if date else DATETIME.TRADING
        wise_date = date if date else DATETIME.WISE        

        latest_path = os.path.join(PROJECT_DATA.tickers, latest_date)
        base_path = os.path.join(PROJECT_DATA.tickers, base_date)
        wise_path = os.path.join(PROJECT_DATA.tickers, wise_date)
        os.makedirs(latest_path, exist_ok=True)
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(wise_path, exist_ok=True)

        self.runners = (
            ("corporations", latest_date, latest_path, tickers.get_corporations),
            ("marketcaps", base_date, base_path, tickers.get_market_caps),
            ("foreignrate", base_date, base_path, tickers.get_foreigner_rate),
            ("sectors", wise_date, wise_path, tickers.get_sectors)
        )
        return

    def fetch(self):
        for file, date, path, func in self.runners:
            stime = time.perf_counter()
            if self.log:
                self.log.info(f'RUN [ FETCH {file.upper()} ] ON {date}')

            if file == 'sectors':
                data = func(date, logger=self.log)
            elif file == 'corporations':
                data = func()
            else:
                data = func(date)
            data.to_parquet(os.path.join(path, f'{file}.parquet'), engine='pyarrow')

            if self.log:
                self.log.info(f'END [ FETCH {file.upper()} ] {time.perf_counter() - stime:.2f}s')
        return