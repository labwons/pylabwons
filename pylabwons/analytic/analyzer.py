from pylabwons.analytic.loader import Ticker, Tickers
from pylabwons.analytic.graphic import layout, xaxis, yaxis, legend

from pandas import DataFrame
from plotly.graph_objs import Figure, Scatter, Candlestick
import pandas as pd


def returns(ta:DataFrame):
    data = []
    for col in ta:
        if col.endswith("Return"):
            ret = ta[col].dropna()
            est = ret.describe()
            est["pos"] = len(ret[ret > 0])
            est["neg"] = len(ret[ret < 0])
            est['pos%'] = 100 * est["pos"] / est["count"]
            for n in [5, 8, 10, 12]:
                est[f'> {n}%'] = 100 * len(ret[ret > n]) / est['count']
            data.append(est)
    return pd.concat(data, axis=1)


class TickerAnalyzer:

    def __init__(self, ticker:Ticker):
        self.o = ticker
        return

    def correlation(self, y1:str, y2:str):
        return self.o.ta[y1].corr(self.o.ta[y2])

    def display_scatter(self, x:str, y:str) -> Figure:
        fig = Figure()

        return fig

    def display_ohlc(self, sig_axis:str=''):
        fig = Figure()
        data = self.o.ohlcv.copy()
        ohlc = Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
        )
        fig.add_trace(ohlc)
        fig.update_layout(layout(
            xaxis=xaxis(),
            yaxis=yaxis(),
            legend=legend()
        ))
        return fig




if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    # obj = TickerAnalyzer('005930')
    # print(obj.ohlcv)
    # obj.plug(backtest_return, 21, 42, 63, 126)
    # obj.plug(bollinger_band)
    # obj.plug(bollinger_band_squeeze_and_expand, window=252, squeeze_pct=0.1)

    # print(obj.ta.columns)
    # print(obj.correlation('forward1mReturn', 'bollinger_width'))
    # df = obj.ta[obj.ta['bollinger_squeeze_and_expand_long'] > 0]
    # print(df)
    # print(returns(df))