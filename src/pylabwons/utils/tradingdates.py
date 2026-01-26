from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week
from typing import Dict, Union
import re, requests


class TradingDates:

    tz = timezone('Asia/Seoul')
    def __init__(self):
        return

    def __sub__(self, other:int):
        key = f"{self.closed}m{other}"
        if not hasattr(self, key):
            prev = datetime.strptime(self.closed, "%Y%m%d") - timedelta(other)
            setattr(self, key, get_nearest_business_day_in_a_week(prev.strftime("%Y%m%d")))
        return getattr(self, key)

    @classmethod
    def clock(cls, fmt:str="") -> Union[datetime, str]:
        if (fmt == "") or (fmt is None):
            return datetime.now(cls.tz)
        return datetime.now(cls.tz).strftime(fmt)

    @property
    def closed(self) -> str:
        if not self.is_open():
            return self.now
        if not hasattr(self, '_closed'):
            today = (self.clock().date() - timedelta(days=1)).strftime("%Y%m%d")
            setattr(self, '_closed', get_nearest_business_day_in_a_week(today))
        return getattr(self, '_closed')

    @property
    def now(self) -> str:
        if not hasattr(self, '_now'):
            setattr(self, '_now', get_nearest_business_day_in_a_week())
        return getattr(self, '_now')

    @property
    def wise_date(self) -> str:
        if not hasattr(self, '_wise'):
            try:
                html = requests.get('https://www.wiseindex.com/Index/Index#/G1010.0.Components').text
                setattr(self, '_wise', re.compile(r"var\s+dt\s*=\s*'(\d{8})'").search(html).group(1))
            except (IndexError, Exception):
                return ''
        return getattr(self, '_wise')

    def is_open(self) -> bool:
        return (self.clock("%Y%m%d") == self.now) and (900 <= int(self.clock("%H%M")) <= 1530)


if __name__ == "__main__":
    tds = TradingDates()
    tds._now = tds.clock("%Y%m%d")
    tds._closed = "20260123"
    print(tds.now)
    print(tds.is_open())
    print(tds.closed)
    print(tds - 1)
    print(tds - 365)
    print(tds.wise_date)