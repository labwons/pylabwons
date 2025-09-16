from pylabwons.typesys import classproperty

from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week as get_td
from typing import Dict
import re, requests


class DateTime:

    tz = timezone('Asia/Seoul')
    BASE = TODAY = datetime.now(tz).strftime('%Y%m%d')

    @classproperty
    def recent_trading(cls) -> str:
        if not hasattr(cls, f'_td_{cls.TODAY}'):
            try:
                setattr(cls, f'_td_{cls.TODAY}', get_td(cls.TODAY))
            except (KeyError, Exception):
                return ''
        return getattr(cls, f'_td_{cls.TODAY}')

    @classproperty
    def trading(cls) -> str:
        if not hasattr(cls, f'_td_{cls.BASE}'):
            try:
                setattr(cls, f'_td_{cls.BASE}', get_td(cls.BASE))
            except (KeyError, Exception):
                return ''
        return getattr(cls, f'_td_{cls.BASE}')

    @classproperty
    def wise(cls) -> str:
        if cls.BASE == cls.TODAY:
            return cls.get_recent_wise_date()
        else:
            return cls.TRADING

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
        td = datetime.strptime(cls.TRADING, '%Y%m%d')
        return {f'D-{n}': get_td((td - timedelta(n)).strftime("%Y%m%d")) for n in previous_days}

    @classmethod
    def is_market_open(cls) -> bool:
        return (cls.TODAY == cls.TRADING) and (900 <= int(datetime.now(cls.tz).strftime("%H%M")) <= 1530)


if __name__ == "__main__":
    print(DateTime.BASE)
    DateTime.BASE = "20240115"
    print(DateTime.BASE)
    print(DateTime.TODAY)
    # print(DateTime.TRADING)
    # print(DateTime.WISE)
    # print(DateTime.get_previous_trading_dates())
    # print(DateTime.is_market_open())
    # DateTime.delta_today(7)
    # print(DateTime.TODAY)
    # print(DateTime.TRADING)