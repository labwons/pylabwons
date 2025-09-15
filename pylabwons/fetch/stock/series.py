from pylabwons.util.tradingdate import DATETIME

from pandas import DataFrame
from pykrx.stock import (
    get_market_ohlcv_by_date,
    get_exhaustion_rates_of_foreign_investment_by_date
)


def get_ohlcv(ticker:str, **kwargs) -> DataFrame:
    _ohlcv = get_market_ohlcv_by_date(
        fromdate=kwargs['fromdate'] if 'fromdate' in kwargs else '19900101',
        todate=kwargs['todate'] if 'todate' in kwargs else DATETIME.TODAY,
        ticker=ticker,
        freq=kwargs['freq'] if 'freq' in kwargs else 'd'
    )

    trade_stop = _ohlcv[_ohlcv.시가 == 0].copy()
    if not trade_stop.empty:
        _ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
    _ohlcv.index.name = 'date'
    return _ohlcv.rename(columns=dict(시가='open', 고가='high', 저가='low', 종가='close', 거래량='volume'))

def get_foreigner_rate_series(ticker:str, **kwargs) -> DataFrame:
    return get_exhaustion_rates_of_foreign_investment_by_date(
        fromdate=kwargs['fromdate'] if 'fromdate' in kwargs else '19900101',
        todate=kwargs['todate'] if 'todate' in kwargs else DATETIME.TODAY,
        ticker=ticker,
    )

