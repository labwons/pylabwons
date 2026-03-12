from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week
from requests.exceptions import ConnectionError, HTTPError, SSLError
from typing import Union


class TradingDate:

    tz = timezone('Asia/Seoul')
    def __init__(self):
        return

    def __str__(self) -> str:
        return self.latest

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


    def get_closed(self) -> str:
        if self.is_open():
            base = (self.clock().date() - timedelta(days=1)).strftime("%Y%m%d")
        else:
            base = self.clock("%Y%m%d")

        try:
            return get_nearest_business_day_in_a_week(base)
        except (ConnectionError, HTTPError, SSLError, IndexError, Exception):
            return base


    @property
    def closed(self) -> str:
        if not hasattr(self, '_closed'):
            setattr(self, '_closed', self.get_closed())
        return getattr(self, '_closed')

    @closed.setter
    def closed(self, closed:str):
        setattr(self, '_closed', closed)

    @property
    def latest(self) -> str:
        if not hasattr(self, '_latest'):
            try:
                setattr(self, '_latest', get_nearest_business_day_in_a_week())
            except (ConnectionError, HTTPError, SSLError, IndexError, Exception):
                setattr(self, '_latest', self.clock('%Y%m%d'))
        return getattr(self, '_latest')

    def is_open(self) -> bool:
        return (self.clock("%Y%m%d") == self.latest) and (900 <= int(self.clock("%H%M")) <= 1530)


if __name__ == "__main__":
    td = TradingDate()
    print(td)
    print(td.is_open())
    print(td.closed)
    print(td - 1)
    print(td - 365)