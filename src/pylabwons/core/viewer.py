from pandas import DataFrame, Series
from pandas.api.types import is_integer_dtype
from plotly.graph_objs import Figure
from pylabwons.schema import trace
from pylabwons.constants import LAYOUT, LEGEND, XAXIS, YAXIS
from typing import Callable


class TickerView(Figure):

    ohlcv: DataFrame

    def __call__(self, renderer:str='browser'):
        self.view(renderer)
        return

    def __new__(cls, ohlcv:DataFrame):
        cls.ohlcv = ohlcv
        return super().__new__(cls)

    def __init__(self, ohlcv:DataFrame):
        super().__init__(
            layout=LAYOUT(
                legend=LEGEND()
            )
        )

        self.set_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.85, 0.15],
            vertical_spacing=0.01,
        )

        self.update_xaxes(row=1, col=1, patch=XAXIS(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=XAXIS(rangeselector=None))
        self.update_yaxes(row=1, col=1, patch=YAXIS())
        self.update_yaxes(row=2, col=1, patch=YAXIS())

        yhoverformat = ',d' if is_integer_dtype(ohlcv['close']) else 'f'
        self.add_trace(trace.Candles(data=ohlcv, yhoverformat=yhoverformat), row=1, col=1)
        self.add_trace(trace.Volume(data=ohlcv, yhoverformat=',d'), row=2, col=1)
        return

    def initialize(self):
        return

    def add_row(self, col:str='', fdef:Callable=None, **kwargs):
        n_rows = len(self._grid_ref) + 1
        if n_rows < 6:
            row_heights = [0.15] * (n_rows - 1)
            row_heights = [1 - sum(row_heights)] + row_heights
        else:
            raise Exception('최대 행 개수는 5개입니다.')

        super().__init__(layout=self.layout, data=self.data)
        self.set_subplots(
            rows=n_rows, cols=1,
            shared_xaxes=True,
            row_heights=row_heights,
            vertical_spacing=0.01,
        )
        self.update_xaxes(row=n_rows - 1, col=1, showticklabels=False)
        self.update_xaxes(row=n_rows, col=1, patch=XAXIS(rangeselector=None))
        if col:
            data = self.ohlcv[col]
            if fdef is not None:
                self.add_trace(fdef(data=data, **kwargs), row=n_rows, col=1)
            else:
                self.add_trace(trace.Line(data=data, **kwargs), row=n_rows, col=1)
        return

    @property
    def template(self) -> str:
        return self.layout.template

    @template.setter
    def template(self, template: str):
        xaxis = self.layout.xaxis
        xaxis['rangeselector']['bgcolor'] = 'black'
        xaxis['rangeselector']['bordercolor'] = 'lightgrey'
        self.update_xaxes(row=1, col=1, patch=xaxis)
        self.update_layout(
            template=template,
            **LAYOUT(
                plot_bgcolor=None,
                legend=LEGEND()
            )
        )
        return

    def view(self, renderer:str='browser'):
        self.show(renderer)
        return


if __name__ == '__main__':
    viewer = TickerView(DataFrame(columns=['open', 'high', 'low', 'close', 'volume']))
    viewer.template = 'plotly_dark'
    viewer.add_row()