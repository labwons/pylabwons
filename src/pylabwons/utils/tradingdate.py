from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week
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

    @property
    def closed(self) -> str:
        if not self.is_open():
            return self.latest
        if not hasattr(self, '_closed'):
            try:
                today = (self.clock().date() - timedelta(days=1)).strftime("%Y%m%d")
                setattr(self, '_closed', get_nearest_business_day_in_a_week(today))
            except IndexError:
                setattr(self, '_closed', self.clock('%Y%m%d'))
        return getattr(self, '_closed')

    @property
    def latest(self) -> str:
        if not hasattr(self, '_latest'):
            try:
                setattr(self, '_latest', get_nearest_business_day_in_a_week())
            except IndexError:
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