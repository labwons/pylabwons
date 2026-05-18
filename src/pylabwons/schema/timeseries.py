from dateutil.relativedelta import relativedelta
from pandas import DataFrame, Series
from plotly.subplots import make_subplots
import pandas as pd
import plotly.graph_objects as go


class TimeSeries(Series):
    _metadata = ['_mom_yoy', '_unit', '_is_mom_yoy']

    def __init__(self, series: Series, **kwargs):
        super().__init__(
            index=series.index,
            data=series.values,
            name=kwargs.get('name', series.name),
            dtype=kwargs.get('dtype', series.dtype)
        )
        self._mom_yoy = DataFrame()
        self._unit = kwargs.get('unit', '')
        self._is_mom_yoy = 'MoM' in str(self.name) or 'YoY' in str(self.name)
        if self.index.tz:
            self.index = series.index.tz_localize(None)
        return

    @property
    def _constructor(self):
        return TimeSeries

    @property
    def mom(self):
        if self._mom_yoy.empty:
            self._mom_yoy = lw.tools.to_mom_yoy(self)
        return TimeSeries(self._mom_yoy['MoM'], name=f'{self.name}(MoM)', unit='%')

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, unit: str):
        self._unit = unit

    @property
    def yoy(self):
        if self._mom_yoy.empty:
            self._mom_yoy = lw.tools.to_mom_yoy(self)
        return TimeSeries(self._mom_yoy['YoY'], name=f'{self.name}(YoY)', unit='%')

    def ma(self, window: int):
        return TimeSeries(self.rolling(window=window).mean(), name=f'{self.name}({window})', unit=self.unit)

    def show(self, **kwargs) -> go.Figure:
        fig = make_subplots(shared_xaxes=True, specs=[[{"secondary_y": True, "r": -0.06}]])
        fig.update_layout(
            height=kwargs.get('height', 600),
            template=kwargs.get('template', 'plotly_dark'),
            hovermode=kwargs.get('hovermode', 'x unified'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            yaxis2=dict(showgrid=False, zeroline=False)
        )
        fig.add_trace(self.trace(), secondary_y=False)
        if not self._is_mom_yoy:
            fig.add_trace(self.mom.trace(visible='legendonly'), secondary_y=True)
            fig.add_trace(self.yoy.trace(visible='legendonly'), secondary_y=True)
        return fig

    def trace(self, **kwargs) -> go.Scatter:
        trace = go.Scatter(
            name=self.name,
            x=self.index,
            y=self.values,
            mode='lines',
            showlegend=True,
            xhoverformat='%Y-%m-%d',
            hovertemplate=f'{self.name}: %{{y}}{self.unit}<extra></extra>'
        )
        trace.update(kwargs)
        return trace


class TimeSeriesSlicer:
    """
    날짜 시계열 인덱스를 가진 판다스 데이터프레임을 자동으로 슬라이싱하는 클래스입니다.
    마지막 일자 기준 [전체, 1/2, 1/4, ...] 형태로 데이터프레임을 슬라이싱합니다.
    최대 기간은 원본 데이터프레임의 전체 기간입니다.
    """

    def __call__(self) -> DataFrame:
        return pd.concat(self.objs, axis=1)

    def __getitem__(self, key) -> DataFrame:
        return self.objs[key]

    def __init__(self, data: DataFrame, base_months=6):
        """
        :param data: 날짜 시계열 인덱스를 가진 판다스 데이터프레임
        :param base_months: 가장 짧은 슬라이싱 기간 (기본값: 6개월)
        """
        self.data = data.copy()
        self.dates = []
        self.objs = {}

        df, first_date, end_date = data.sort_index(), data.index[0], data.index[-1]
        i = 0
        while True:
            months_to_subtract = base_months * (2 ** i)
            start_date = end_date - relativedelta(months=months_to_subtract)
            self.dates.append(start_date)

            if start_date <= first_date:
                self.objs["ALL"] = df
                break

            sliced_df = df.loc[start_date:end_date]

            if months_to_subtract < 12:
                key_name = f"{months_to_subtract}M"
            else:
                key_name = f"{months_to_subtract // 12}Y"
                if months_to_subtract % 12 != 0:
                    key_name += f" {months_to_subtract % 12}M"

            self.objs[key_name] = sliced_df
            i += 1

        return

    def __iter__(self):
        for key in self.objs:
            yield key, self.objs[key]
