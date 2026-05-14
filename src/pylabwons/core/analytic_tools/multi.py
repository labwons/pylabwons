from pylabwons.schema.timeseries import TimeSeriesSlicer
from pandas import DataFrame
import pandas as pd
import plotly.graph_objects as go


class MultiAssetRelation:
    def __init__(self, ohlcv: DataFrame, basis: str = ''):
        self.ohlcv = ohlcv
        self.basis = ohlcv.columns[0] if not basis else basis
        self.slice = TimeSeriesSlicer(ohlcv, base_months=3)
        return

    @property
    def cumulative_return(self) -> DataFrame:
        objs = {}
        for period, df in self.slice:
            objs[period] = (df.pct_change().fillna(0) + 1).cumprod() - 1
        return round(100 * pd.concat(objs, axis=1), 2)

    @property
    def drawdown(self) -> DataFrame:
        objs = {}
        for period, df in self.slice:
            objs[period] = df / df.cummax() - 1
        return round(100 * pd.concat(objs, axis=1), 2)

    def plotly_multi(self, value_type: str = 'cummulative_return'):
        df = getattr(self, value_type)
        fig = go.Figure()

        # unique한 기간(level 0)과 자산(level 1) 추출
        unique_periods = df.columns.levels[0].tolist()
        unique_assets = df.columns.levels[1].tolist()

        # 데이터프레임의 모든 컬럼을 Trace로 추가
        for period in unique_periods:
            for asset in unique_assets:
                data = df[(period, asset)].dropna()
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data,
                        mode="lines",
                        name=asset,
                        showlegend=True,
                        visible=True if period == unique_periods[0] else False,
                        xhoverformat="%Y-%m-%d",
                        hovertemplate=f"{asset}: %{{y:.2f}}%<extra></extra>",
                    )
                )

        buttons = []
        for target_period in unique_periods:
            visible_mask = []
            for period in unique_periods:
                for asset in unique_assets:
                    if period == target_period:
                        visible_mask.append(True)
                    else:
                        visible_mask.append(False)

            # 버튼 정의
            buttons.append(
                dict(
                    label=target_period,
                    method="update",
                    args=[
                        {"visible": visible_mask},  # Trace 가시성 업데이트
                    ],
                )
            )

        # 4. 레이아웃에 버튼 및 디자인 적용
        fig.update_layout(
            template="plotly_dark",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.01,  # 왼쪽 상단 위치
                    xanchor="left",
                    y=1.15,
                    yanchor="top",
                )
            ],
            yaxis_title="[%]",
            xaxis=dict(
                tickformat="%Y-%m-%d",
            )
        )
        return fig

if __name__ == "__main__":
    mar = MultiAssetRelation(asset.xs('close', axis=1, level=1))
    # mar.basis
    # mar.slice
    # mar.cummulative_return
    # mar.drawdown
    fig = mar.plotly_multi('drawdown')
    fig.update_layout(
        height=600
    )