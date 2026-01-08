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

    def serialize(self, n:int, **mask) -> DataFrame:
        cols = [f'return{n}High', f'return{n}Low', f'return{n}Mid']
        base = self._inst.serialize() if self._is_bundle else self._inst
        if 'ticker' in base:
            cols.append('ticker')
        if mask:
            for k, v in mask.items():
                base = base[base[k] == v]
        return base[cols].copy()

    def report(self, n:int, **mask) -> DataFrame:
        src = self.serialize(n, **mask)
        if 'ticker' in src.columns:
            src.drop(columns=['ticker'], inplace=True)

        desc = src.describe().T
        desc.drop(columns=["std", "25%", "75%"], inplace=True)
        desc['count'] = desc['count'].astype(int)
        desc = desc.rename(columns={
            'mean': 'meanReturn', 'min': 'minReturn', 'max': 'maxReturn', '50%': 'medianReturn',
        })
        desc[">= 5%"] = [len(src[src[col] >= 0.05]) / desc.loc[col, 'count'] for col in src]
        desc[">= 4%"] = [len(src[src[col] >= 0.04]) / desc.loc[col, 'count'] for col in src]
        desc[">= 3%"] = [len(src[src[col] >= 0.03]) / desc.loc[col, 'count'] for col in src]
        desc[">= 0%"] = [len(src[src[col] >= 0]) / desc.loc[col, 'count'] for col in src]
        desc[">= mean%"] = [len(src[src[col] >= src[col].mean()]) / desc.loc[col, 'count'] for col in src]
        return desc

    def view_gaussian(self, n:int, **mask):
        src = self.serialize(n, **mask)
        for col in src:
            if col == 'ticker':
                continue
            dat = src[col]
            src[f'{col}-Normalized'] = Series(
                index=dat.index,
                data=norm.pdf(dat, dat.mean(), dat.std()),
            )

        fig = Figure()
        for col in src:
            if col.endswith('Normalized') or col == 'ticker':
                continue
            if col.lower().endswith('high'):
                color = 'red'
            elif col.lower().endswith('low'):
                color = 'royalblue'
            else:
                color = 'green'
            dat = src.sort_values(by=col, ascending=True)
            if len(dat) > 5e+4:
                dat = dat.iloc[::int(len(dat) // 5e+4)]
            text = dat['ticker'] if 'ticker' in dat.columns else None
            hovertemplate = '%{x:.2f}% @%{meta}<extra></extra>'
            if text is not None:
                hovertemplate = '%{text}: ' + hovertemplate
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
                    text=text,
                    meta=dat.index,
                    hovertemplate=hovertemplate
                )
            )
            avg = 100 * dat[col].mean()
            fig.add_vline(x=avg, line_color=color, line_width=0.8, line_dash='dash')
        fig.show('browser')
        return



