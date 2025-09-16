from pylabwons.typesys import classproperty

from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week as get_td
from typing import Dict
import re, requests


class DateTime:

    tz = timezone('Asia/Seoul')
    base = today = datetime.now(tz).strftime('%Y%m%d')

    @classproperty
    def recent_trading(cls) -> str:
        if not hasattr(cls, f'_td_{cls.today}'):
            try:
                setattr(cls, f'_td_{cls.today}', get_td(cls.today))
            except (KeyError, Exception):
                return ''
        return getattr(cls, f'_td_{cls.today}')

    @classproperty
    def trading(cls) -> str:
        if not hasattr(cls, f'_td_{cls.base}'):
            try:
                setattr(cls, f'_td_{cls.base}', get_td(cls.base))
            except (KeyError, Exception):
                return ''
        return getattr(cls, f'_td_{cls.base}')

    @classproperty
    def wise(cls) -> str:
        if cls.base == cls.today:
            return cls.get_recent_wise_date()
        else:
            return cls.trading

    @classmethod
    def get_recent_wise_date(cls) -> str:
        if not hasattr(cls, '_wise'):
            try:
                html = requests.get('https://www.wiseindex.com/Index/Index#/G1010.0.Components').text
                setattr(cls, '_wise', re.compile(r"var\s+dt\s*=\s*'(\d{8})'").search(html).group(1))
            except (IndexError, Exception):
                return ''
        return getattr(cls, '_wise')

    @classmethod
    def get_previous_trading_dates(cls, *previous_days) -> Dict[str, str]:
        if not previous_days:
            previous_days = [1, 7, 14, 30, 61, 92, 183, 365]
        td = datetime.strptime(cls.trading, '%Y%m%d')
        return {f'D-{n}': get_td((td - timedelta(n)).strftime("%Y%m%d")) for n in previous_days}

    @classmethod
    def is_market_open(cls) -> bool:
        return (cls.today == cls.trading) and (900 <= int(datetime.now(cls.tz).strftime("%H%M")) <= 1530)

    @classmethod
    def use_closed_market(cls):
        if cls.is_market_open():
            cls.base = (datetime.now(cls.tz) - timedelta(1)).strftime('%Y%m%d')
        return


if __name__ == "__main__":
    print(DateTime.base)
    DateTime.base = "20240115"
    print(DateTime.base)
    print(DateTime.today)
    # print(DateTime.TRADING)
    # print(DateTime.WISE)
    # print(DateTime.get_previous_trading_dates())
    # print(DateTime.is_market_open())
    # print(DateTime.today)
    # print(DateTime.trading)