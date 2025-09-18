from pylabwons.util.tradingdate import TradingDate
from pylabwons.util.path import ARCHIVE

from pandas import DataFrame
from pykrx.stock import (
    get_market_ohlcv_by_date,
    get_market_cap_by_date,
    get_exhaustion_rates_of_foreign_investment_by_date
)
from time import sleep
import os


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
    TRY_COUNT = 5
    logger = kwargs['logger'] if "logger" in kwargs else None
    sizeof = len(tickers)
    for n, ticker in enumerate(tickers):
        index = f'{n + 1}/{sizeof}'.zfill(len(str(sizeof)) * 2 + 1)
        if logger:
            logger.info(f'FETCH OHLCV: {ticker} ... ({index})')
        for m in range(1, TRY_COUNT + 1, 1):
            try:
                ohlcv = get_ohlcv(ticker=ticker, **kwargs)
                if ohlcv.empty:
                    raise Exception
                file = os.path.join(ARCHIVE.ohlcv, f'{ticker}.pkl')
                ohlcv.to_pickle(ARCHIVE.create(file))
                break
            except (AttributeError, KeyError, ValueError, Exception):
                if logger:
                    logger.info(f'>>> RETRY FETCHING OHLCV: {ticker} ... {m}')
                sleep(5)
                        
            if m == TRY_COUNT and logger:
                logger.info(f'>>> FAILED TO FETCH OHLCV FOR TICKER: {ticker}')
                


