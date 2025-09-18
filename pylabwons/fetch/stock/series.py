from pylabwons.util.tradingdate import TradingDate

from pandas import DataFrame
from pykrx.stock import (
    get_market_ohlcv_by_date,
    get_market_cap_by_date,
    get_exhaustion_rates_of_foreign_investment_by_date
)

RENAMER = {
    "시가": "open", "고가": "high", "저가": "low", "종가": "close", "거래량": "volume",
    "시가총액": "marketCap", "거래대금":"amount", "상장주식수":"shares",
    "지분율": "sharesRate", "한도소진률":"exhaustionRate"
}

def get_ohlcv(ticker:str, **kwargs) -> DataFrame:
    data = get_market_ohlcv_by_date(
        fromdate=kwargs['fromdate'] if 'fromdate' in kwargs else '19900101',
        todate=kwargs['todate'] if 'todate' in kwargs else TradingDate.recent_closed,
        ticker=ticker,
        freq=kwargs['freq'] if 'freq' in kwargs else 'd'
    )

    trade_stop = data[data.시가 == 0].copy()
    if not trade_stop.empty:
        data.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
    data.index.name = 'date'
    data = data.drop(columns=[c for c in data if not c in RENAMER])
    data = data.rename(columns={c:RENAMER[c] for c in data if c in RENAMER})
    return data

def get_market_cap(ticker:str, **kwargs) -> DataFrame:
    data = get_market_cap_by_date(
        fromdate=kwargs['fromdate'] if 'fromdate' in kwargs else '19900101',
        todate=kwargs['todate'] if 'todate' in kwargs else TradingDate.recent_closed,
        ticker=ticker,
        freq=kwargs['freq'] if 'freq' in kwargs else 'd'
    )
    data.index.name = 'date'
    data = data.drop(columns=[c for c in data if not c in RENAMER])
    data = data.rename(columns={c:RENAMER[c] for c in data if c in RENAMER})
    return data

def get_foreigner_rate(ticker:str, **kwargs) -> DataFrame:
    data = get_exhaustion_rates_of_foreign_investment_by_date(
        fromdate=kwargs['fromdate'] if 'fromdate' in kwargs else '19900101',
        todate=kwargs['todate'] if 'todate' in kwargs else TradingDate.recent_closed,
        ticker=ticker,
    )
    data.index.name = 'date'
    data = data.drop(columns=[c for c in data if not c in RENAMER])
    data = data.rename(columns={c:RENAMER[c] for c in data if c in RENAMER})
    return data


def backfill(*tickers, **kwargs):
    logger = kwargs['logger'] if "logger" in kwargs else None

