from pylabwons.analytic.loader import Ticker, Tickers
from pylabwons.analytic.graphic import layout, xaxis, yaxis, legend

from pandas import DataFrame
from plotly.graph_objs import Figure, Scatter, Candlestick
from typing import Union
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

    def __init__(self, ticker:Union[Ticker, str]):
        if isinstance(ticker, str):
            ticker = Ticker(ticker)
        self.o = ticker
        return

    def correlation(self, y1:str, y2:str):
        return self.o.ta[y1].corr(self.o.ta[y2])

    def display_scatter(self, x:str, y:str) -> Figure:
        fig = Figure()

        return fig

    def display_ohlc(self, *axes:str):
        fig = Figure()
        data = self.o.ohlcv.copy()
        ohlc = Candlestick(
            name=f'{self.o["name"]}({self.o.ticker})',
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            showlegend=True,
            increasing={
                "fillcolor":"red",
                "line_color":"red"
            },
            decreasing={
                "fillcolor": "blue",
                "line_color": "blue"
            },
            text=[f'{i.strftime("%Y/%m/%d")}<br>open: {o:,d}<br>high: {h:,d}<br>low: {l:,d}<br>close: {c:,d}' for i, o, h, l, c, v in data.itertuples()],
            hoverinfo="text"

        )
        fig.add_trace(ohlc)

        marker_size = 11
        for axis in axes:
            sig = self.o.ta[axis] * self.o.ta['low']
            scatter = Scatter(
                x=sig.index,
                y=sig.values,
                name=axis,
                mode='markers',
                marker={
                    "symbol":"triangle-up",
                    "size": marker_size,
                    "color": "green"
                },
                xhoverformat="%Y/%m/%d",
                hovertemplate="%{y:,d}@%{x}<extra></extra>"
            )
            fig.add_trace(scatter)
        fig.update_layout(layout(
            xaxis=xaxis(),
            yaxis=yaxis(),
            legend=legend()
        ))
        return fig




if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    obj = TickerAnalyzer('005930')
    obj.display_ohlc().show('browser')
    # print(obj.ohlcv)
    # obj.plug(backtest_return, 21, 42, 63, 126)
    # obj.plug(bollinger_band)
    # obj.plug(bollinger_band_squeeze_and_expand, window=252, squeeze_pct=0.1)

    # print(obj.ta.columns)
    # print(obj.correlation('forward1mReturn', 'bollinger_width'))
    # df = obj.ta[obj.ta['bollinger_squeeze_and_expand_long'] > 0]
    # print(df)
    # print(returns(df))