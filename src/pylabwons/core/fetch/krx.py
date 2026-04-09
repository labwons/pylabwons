from datetime import datetime, timedelta
from pandas import concat, Series, DataFrame
from pykrx.stock import get_market_ohlcv_by_date, get_market_cap_by_date


def get_ohlcv(**kwargs) -> DataFrame:
    ohlcv = get_market_ohlcv_by_date(**kwargs)
    trade_stop = ohlcv[ohlcv.시가 == 0].copy()
    if not trade_stop.empty:
        ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
    ohlcv.index.name = 'date'
    return ohlcv.rename(columns=dict(시가='open', 고가='high', 저가='low', 종가='close', 거래량='volume'))[[
        'open', 'high', 'low', 'close', 'volume'
    ]]

def get_market_cap(**kwargs) -> DataFrame:
    return get_market_cap_by_date(**kwargs)

#
# class PyKrx:
#     """
#     Fetch source data from PyKrx (through <package; pyPyKrx>)
#
#     @ohlcv
#         constraint  : common
#         type        : DataFrame
#         description : stock price (open, high, low, close) and volume
#         columns     : ["open", "high", "low", "close", "volume"]
#         example     :
#                          open   high    low  close    volume
#             date
#             2013-12-13  28200  28220  27800  27800    201065
#             2013-12-16  27820  28080  27660  28000    179088
#             2013-12-17  28340  28340  27860  27900    155248
#             ...           ...    ...    ...    ...       ...
#             2023-12-07  71800  71900  71100  71500   8862017
#             2023-12-08  72100  72800  71900  72600  10859463
#             2023-12-11  72800  73000  72200  73000   9406504
#
#     @quarterlyMarketCap
#         constraint  : stock only
#         type        : Series
#         description : quarterly market cap
#         example     :
#               month
#             2019/03     93522
#             2019/06     95563
#             2019/09     89922
#                 ...       ...
#             2023/03     83071
#             2023/06     85838
#             2023/09     93241
#             2023/11     95497
#             Name: marketCap, dtype: int32
#     """
#
#     def __init__(self, ticker:str, period:int=10, freq:str="d"):
#         self.ticker = ticker
#         self.period = period
#         self.freq = freq
#         return
#
#     def getMarketCap(self) -> DataFrame:
#         if not hasattr(self, "__cap"):
#             cap = get_market_cap_by_date(
#                 fromdate=(datetime.today() - timedelta(365 * 8)).strftime("%Y%m%d"),
#                 todate=datetime.today().strftime("%Y%m%d"),
#                 freq='m',
#                 ticker=self.ticker
#             )
#             self.__setattr__("__cap", cap)
#         return self.__getattribute__("__cap")
#
#     @classmethod
#     def get_multi_ohlcv(cls, tickers: list, period: int = 5, freq: str = 'd') -> DataFrame:
#         todate = datetime.today().strftime("%Y%m%d")
#         frdate = (datetime.today() - timedelta(365 * period)).strftime("%Y%m%d")
#         objs = {}
#         for tic in tickers:
#             ohlcv = get_market_ohlcv_by_date(
#                 fromdate=frdate,
#                 todate=todate,
#                 ticker=tic,
#                 freq=freq
#             )
#
#             trade_stop = ohlcv[ohlcv.시가 == 0].copy()
#             if not trade_stop.empty:
#                 ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
#             ohlcv.index.name = 'date'
#             objs[tic] = ohlcv.rename(columns=dict(시가='open', 고가='high', 저가='low', 종가='close', 거래량='volume'))
#         return concat(objs, axis=1)
#
#     @property
#     def ohlcv(self) -> DataFrame:
#         todate = datetime.today().strftime("%Y%m%d")
#         frdate = (datetime.today() - timedelta(365 * self.period)).strftime("%Y%m%d")
#         ohlcv = get_market_ohlcv_by_date(
#             fromdate=frdate,
#             todate=todate,
#             ticker=self.ticker,
#             freq=self.freq
#         )
#
#         trade_stop = ohlcv[ohlcv.시가 == 0].copy()
#         if not trade_stop.empty:
#             ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
#         ohlcv.index.name = 'date'
#         return ohlcv.rename(columns=dict(시가='open', 고가='high', 저가='low', 종가='close', 거래량='volume'))[[
#             'open', 'high', 'low', 'close', 'volume'
#         ]]
#
#     @property
#     def quarterlyMarketCap(self) -> Series:
#         cap = self.getMarketCap()
#         cap = cap[
#             cap.index.astype(str).str.contains('03') | \
#             cap.index.astype(str).str.contains('06') | \
#             cap.index.astype(str).str.contains('09') | \
#             cap.index.astype(str).str.contains('12') | \
#             (cap.index == cap.index[-1])
#         ]
#         cap.index = cap.index.strftime("%Y/%m")
#         cap.index = [
#             col.replace("03", "1Q").replace("06", "2Q").replace("09", "3Q").replace("12", "4Q") for col in cap.index
#         ]
#         cap.index.name = "quarter"
#         return Series(index=cap.index, data=cap['시가총액'] / 100000000, dtype=int)
#
#     @property
#     def yearlyMarketCap(self) -> Series:
#         cap = self.getMarketCap()
#         cap = cap[cap.index.astype(str).str.contains('12') | (cap.index == cap.index[-1])]
#         cap.index = cap.index.strftime("%Y/%m")
#         cap.index.name = "year"
#         return Series(index=cap.index, data=cap['시가총액'] / 100000000, dtype=int)
#
#
#
# if __name__ == "__main__":
#     from pandas import set_option
#     set_option('display.expand_frame_repr', False)
#
#     pyKrx = PyKrx(
#         "005930"
#         # "069500"
#     )
#     print(PyKrx.ohlcv)
#     print(PyKrx.quarterlyMarketCap)
