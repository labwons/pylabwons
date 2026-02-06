from pandas import DataFrame
import functools


GENERAL = dict(
    회사명="name",
    시장구분='market',
    업종='krxIndustry',
    주요제품='krxProduct',
    상장일='ipo',
)

MARKET_CAP = dict(
    종가='close',
    시가총액='marketCap',
    거래량='volume',
    거래대금='amount',
    상장주식수='shares'
)

MULTIPLES = dict(
    BPS='quarterlyBps',
    PER='quarterlyPE',
    PBR='quarterlyPB',
    EPS='quarterlyEps',
)

FOREIGN_RATE = dict(
    보유수량='foreignSharesHolding',
    지분율='foreignRate',
    한도수량='foreignSharesLimit',
    한도소진률='foreignRateByLimit'
)

KRX_GENERAL = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'

YIELD_DAYS = dict(
    returnOn1Day=1,
    returnOn1Week=7,
    returnOn1Month=30,
    returnOn3Months=91,
    returnOn6Months=183,
    returnOn1Year=365,
)

def marketfetch(name):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(cls, *args, **kwargs):
            if hasattr(cls, 'logger') and cls.logger:
                cls.logger(f"FETCH [{name}]", end=" ... ")

            try:
                result = func(cls, *args, **kwargs)

                if hasattr(cls, 'logger') and cls.logger:
                    cls.logger(f"OK")
                return result

            except Exception as e:
                if hasattr(cls, 'logger') and cls.logger:
                    cls.logger(f"NG: {e}")
                return DataFrame()

        return wrapper

    return decorator