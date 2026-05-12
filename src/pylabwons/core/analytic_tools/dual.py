from pandas import DataFrame, Series
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools as ts
import plotly.graph_objects as go


class DualRelation:

    def __init__(
            self,
            indicator: Series,
            asset: Series,
            **kwargs
    ):
        self.indicator = indicator
        self.asset = asset
        if indicator.name == asset.name:
            indicator.name = 'indicator'
            asset.name = 'asset'

        self.unit = unit = 'm' if indicator.index.diff().min().days >= 20 else 'd'
        if unit == 'm':
            sampler = 'MS' if indicator.index[0].day == 1 else 'ME'
            self.data = pd.concat([indicator, asset.resample(sampler).last()], axis=1).dropna()
        else:
            self.data = pd.concat([indicator, asset], axis=1).dropna()
        self.data.columns = [kwargs.get('indicator_name', indicator.name), kwargs.get('asset_name', asset.name)]
        self.window = kwargs.get('window', 6 if unit == 'd' else 24)
        self.max_lag = kwargs.get('max_lag', 20 if unit == 'd' else 6)
        return

    @property
    def corr(self) -> DataFrame:
        """
        두 시계열 데이터(a, b) 간의 시차 상관계수(CCF)를 계산하여 선/후행 관계를 분석하는 함수

        * NOTE
        데이터 변환       : 데이터를 로그 수익률로 변환, 시계열의 안정성(Stationarity) 확보
        슬라이딩 윈도우   : window_months 만큼 rolling하여 분석, 시간에 따른 자산 간 관계 변형 포착
        CCF(교차 상관계수): ts.ccf를 이용해 A가 n일 전/후의 움직임으로 B를 얼마나 설명하는지 수치화
        우세 관계 판별    : 선행, 후행, 동행 지표 중 절댓값이 가장 큰 항목으로 해당 시계열의 두 자산의 관계 정의
        """
        k1, k2 = self.data.columns
        df_ret = np.log(self.data / self.data.shift(1)).dropna()
        if df_ret.empty:
            return DataFrame()

        results = []
        indices = []

        # 기준 날짜들을 df_ret(수익률) 인덱스 기준으로 설정하여 정렬 유지
        available_dates = df_ret.index
        curr_end = available_dates[-1]
        first_date = available_dates[0]

        expanding_corr = self.data[k1].expanding().corr(self.data[k2])
        while curr_end >= first_date + pd.DateOffset(months=self.window):
            curr_start = curr_end - pd.DateOffset(months=self.window)

            # 윈도우 슬라이싱 (인덱스 범위 기반)
            period_ret = df_ret.loc[curr_start:curr_end]

            if len(period_ret) > 3 * self.max_lag:
                ser_a = period_ret[k1]
                ser_b = period_ret[k2]

                # --- CCF 분석 ---
                ccf_a_leads_b = ts.ccf(ser_a, ser_b, adjusted=True)[:self.max_lag + 1]
                ccf_b_leads_a = ts.ccf(ser_b, ser_a, adjusted=True)[:self.max_lag + 1]

                sync = ccf_a_leads_b[0]
                leading_vals = ccf_a_leads_b[1:]
                leading_idx = np.argmax(np.abs(leading_vals)) + 1
                leading = leading_vals[leading_idx - 1]

                lagging_vals = ccf_b_leads_a[1:]
                lagging_idx = np.argmax(np.abs(lagging_vals)) + 1
                lagging = lagging_vals[lagging_idx - 1]

                # --- 상관계수 추출 (에러 방지를 위해 get_loc 또는 asof 사용) ---
                # curr_end 시점에 가장 가까운 과거의 누적 상관계수 값을 가져옴
                cum_corr = expanding_corr.asof(curr_end)

                # 윈도우 내 Raw 상관계수
                window_raw_df = self.data.loc[curr_start:curr_end]
                window_raw_corr = window_raw_df[k1].corr(window_raw_df[k2])

                result = {
                    'leading': leading,
                    f'leading_diff({self.unit})': leading_idx,
                    'lagging': lagging,
                    f'lagging_diff({self.unit})': lagging_idx,
                    'synchronous(ccf)': sync,
                    'cumulative(raw)': cum_corr,
                    'synchronous(raw)': window_raw_corr
                }

                # 판별 로직
                if max(abs(leading), abs(lagging), abs(sync)) < 0.25:
                    result['relation'] = 'low correlation'
                elif abs(leading) > abs(sync) and abs(leading) > abs(lagging):
                    result['relation'] = f'{leading_idx}{self.unit} leading'
                elif abs(lagging) > abs(sync) and abs(lagging) > abs(leading):
                    result['relation'] = f'{lagging_idx}{self.unit} lagging'
                else:
                    result['relation'] = 'synchronous'

                results.append(result)
                indices.append(f"{curr_start.strftime('%Y/%m')}-{curr_end.strftime('%Y/%m')}")  # 인덱스를 종료일자로 명확히 표기

            curr_end = curr_end - pd.DateOffset(months=int(self.window / 2))
            if curr_end >= first_date:
                curr_end = available_dates[available_dates <= curr_end][-1]

        return DataFrame(results, index=indices)

    def plotly(self, **kwargs):
        name_1, name_2 = self.data.columns
        s1 = self.data[name_1]
        s2 = self.data[name_2]
        color1 = kwargs.get('color1', '#1f77b4')  # tab:blue
        color2 = kwargs.get('color2', '#ff7f0e')  # tab:orange
        title = kwargs.get('title', f'{name_1} vs {name_2}')

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=s1,
                name=name_1,
                line=dict(color=color1),
                xhoverformat='%Y-%m-%d',
                hovertemplate=f'{name_1}: %{{y}}<extra></extra>'
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=s2.index,
                y=s2,
                name=name_2,
                line=dict(color=color2),
                xhoverformat='%Y-%m-%d',
                hovertemplate=f'{name_2}: %{{y}}<extra></extra>'
            ),
            secondary_y=True,
        )

        # 3. 레이아웃 업데이트 (다크 모드 및 스타일)
        fig.update_layout(
            title_text=title,
            height=700,
            template='plotly_dark',
            hovermode='x unified',  # 마우스 오버 시 두 데이터 동시에 표시
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # 축 이름 설정
        fig.update_yaxes(title_text=name_1, color=color1, secondary_y=False)
        fig.update_yaxes(title_text=name_2, color=color2, secondary_y=True)

        return fig

if __name__ == "__main__":
    import plotly.io as pio
    pio.renderers.default = "vscode"
