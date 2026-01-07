from pandas import DataFrame, Series
from pandas.api.types import is_integer_dtype
from plotly.graph_objs import Figure
from pylabwons.schema import trace
from pylabwons.constants import LAYOUT, LEGEND, XAXIS, YAXIS


class TickerView:

    def __init__(self, ohlcv:DataFrame):
        fig = Figure()
        fig.set_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.85, 0.15],
            vertical_spacing=0.01,
        )

        fig.update_layout(LAYOUT(legend=LEGEND()))
        fig.update_xaxes(row=1, col=1, patch=XAXIS(showticklabels=False))
        fig.update_yaxes(row=1, col=1, patch=YAXIS())
        fig.update_xaxes(row=2, col=1, patch=XAXIS(rangeselector=None))

        yhoverformat = ',d' if is_integer_dtype(ohlcv['close']) else 'f'
        fig.add_trace(trace.Candles(data=ohlcv, yhoverformat=yhoverformat), row=1, col=1)
        fig.add_trace(trace.Volume(data=ohlcv, yhoverformat=',d'), row=2, col=1)

        self.fig = fig
        self.ohlcv = ohlcv.copy()
        return

    def view_signal(self, signal_name:str, signal:Series, **kwargs):
        if signal.dtype == bool:
            signal = signal[signal == True]
            signal = self.ohlcv[self.ohlcv.index.isin(signal.index)]['low']
        self.fig.add_trace(trace.Marker(signal, name=signal_name, **kwargs))
        return

    def view_indicator(self, data:Series, row=1, col=1, **kwargs):
        self.fig.add_trace(trace.Line(data=data, **kwargs), row=row, col=col)
        return

    def view(self):
        self.fig.show('browser')
        return