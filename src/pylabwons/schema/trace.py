from pandas import DataFrame, Series
from plotly.graph_objs import Bar, Candlestick, Scatter
from typing import Any, Union
from pylabwons.constants import RISE, FALL

xhoverformat = '%Y/%m/%d %H:%M:%S'
class Candles(Candlestick):

    def __init__(self, data:DataFrame, **kwargs:Any):
        yhoverformat = ',d' if all(str(n).endswith('.0') for n in data['close'][-5:]) else 'f'
        yhoverformat = kwargs.get('yhoverformat', yhoverformat)
        super().__init__(
            name=kwargs.get('name', ''),
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            visible=kwargs.get('visible', True),
            showlegend=kwargs.get('showlegend', False),
            increasing_line={'color':RISE},
            decreasing_line={'color':FALL},
            hoverinfo='x+y',
            xhoverformat=xhoverformat,
            yhoverformat=yhoverformat,
            hovertemplate=(
                f"시가: %{{open:{yhoverformat}}}<br>" +
                f"고가: %{{high:{yhoverformat}}}<br>" +
                f"저가: %{{low:{yhoverformat}}}<br>" +
                f"종가: %{{close:{yhoverformat}}}<extra></extra>"
            )
        )
        self.update(**kwargs)
        return


class Volume(Bar):

    def __init__(self, data:DataFrame, **kwargs:Any):
        super().__init__(
            name=f'Vol',
            x=data.index,
            y=data['volume'],
            visible=kwargs.get('visible', True),
            showlegend=kwargs.get('showlegend', False),
            marker={
                'color': data.apply(lambda r: RISE if r["close"] >= r["open"] else FALL, axis=1)
            },
            xhoverformat="%Y/%m/%d",
            yhoverformat=",d",
            hovertemplate="%{y}<extra></extra>"
        )
        self.update(**kwargs)
        return


class Line(Scatter):

    def __init__(self, data:Series, **kwargs:Any):
        super().__init__(
            name=kwargs.get('name', data.name),
            x=data.index,
            y=data,
            mode="lines",
            visible=kwargs.get('visible', True),
            showlegend=kwargs.get('showlegend', False),
            xhoverformat=xhoverformat,
            yhoverformat=kwargs.get('yhoverformat', '.2f'),
            hovertemplate=f"{kwargs.get('name', data.name)}: %{{y}}<extra></extra>",
        )
        self.update(**kwargs)
        return


class Marker(Scatter):

    def __init__(self, data:Series, **kwargs:Any):
        super().__init__(
            name=kwargs.get('name', data.name),
            x=data.index,
            y=data.values,
            mode="markers",
            visible=kwargs.get('visible', True),
            showlegend=kwargs.get('showlegend', False),
            marker={
                'symbol':kwargs.get('symbol', 'triangle-up'),
                'size': kwargs.get('size', 10),
                'color': kwargs.get('color', RISE)
            },
            xhoverformat=xhoverformat,
            yhoverformat=kwargs.get('yhoverformat', '.2f'),
            hovertemplate=f"{kwargs.get('name', data.name)}: %{{y}}<extra></extra>",
        )