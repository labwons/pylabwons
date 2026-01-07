from pandas import DataFrame, Series
from plotly.graph_objs import Figure, Scatter
from pylabwons.core.detector import Detector
from pylabwons.core.viewer import TickerView
from scipy.stats import norm
from typing import Any, Union


class BackTester(Detector, TickerView):

    def __init__(self, ohlcv: Union[Any, DataFrame]):
        if not isinstance(ohlcv, DataFrame):
            try:
                ohlcv = getattr(ohlcv, 'ohlcv')
            except AttributeError:
                raise TypeError()
        Detector.__init__(self, ohlcv)
        if not self._is_bundle:
            TickerView.__init__(self, ohlcv)
        return

    def calc_return(self, n:int):
        base = self._inst['close'].shift(n - 1)
        high = (self._inst['high'].rolling(n - 1).max() / base - 1).shift(-n + 1)
        low = (self._inst['low'].rolling(n - 1).min() / base - 1).shift(-n + 1)
        mid = (high + low) / 2
        self[f'return{n}High'] = high
        self[f'return{n}Low'] = low
        self[f'return{n}Mid'] = mid
        return

    def evaluate(self, signal_name:str, n:int) -> DataFrame:
        cols = [f'return{n}High', f'return{n}Low', f'return{n}Mid']
        base = self._inst.stack if self._is_bundle else self._inst
        if 'ticker' in base:
            cols.append('ticker')
        return base[base[signal_name] == True][cols].copy()

    def report(self, signal_name:str, n:int) -> DataFrame:
        src = self.evaluate(signal_name, n)
        if 'ticker' in src.columns:
            src.drop(columns=['ticker'], inplace=True)
        cnt = len(src)
        desc = src.describe().T
        desc.drop(columns=["25%", "50%"], inplace=True)
        desc[">= 4%"] = [len(src[src[col] >= 0.04]) / cnt for col in src]
        desc[">= 0%"] = [len(src[src[col] >= 0]) / cnt for col in src]
        desc["< 0%"] = [len(src[src[col] < 0]) / cnt for col in src]
        desc[">= mean%"] = [len(src[src[col] >= src[col].mean()]) / cnt for col in src]
        desc["< mean%"] = [len(src[src[col] < src[col].mean()]) / cnt for col in src]
        return desc

    def view_gaussian(self, signal_name:str, n:int):
        src = self.evaluate(signal_name, n)
        if 'ticker' in src.columns:
            src.drop(columns=['ticker'], inplace=True)
        for col in src:
            dat = src[col]
            src[f'{col}-Normalized'] = Series(
                index=dat.index,
                data=norm.pdf(dat, dat.mean(), dat.std()),
            )

        fig = Figure()
        for col in src:
            if col.endswith('Normalized'):
                continue
            if col.lower().endswith('high'):
                color = 'red'
            elif col.lower().endswith('low'):
                color = 'royalblue'
            else:
                color = 'green'
            dat = src.sort_values(by=col, ascending=True)
            fig.add_trace(
                Scatter(
                    name=col,
                    x=100 * dat[col],
                    y=dat[f'{col}-Normalized'],
                    visible=True,
                    showlegend=False,
                    mode='lines+markers',
                    marker={
                        'symbol': 'circle',
                        'color': color
                    },
                    line={
                        'color': color,
                    },
                    meta=dat.index,
                    hovertemplate='%{x:.2f}%@%{meta}<extra></extra>'
                )
            )
            avg = 100 * dat[col].mean()
            fig.add_vline(x=avg, line_color=color, line_width=0.8, line_dash='dash')
        fig.show('browser')
        return



