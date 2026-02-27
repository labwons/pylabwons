from pylabwons.core.fetch.stock import _schema as SCHEMA
from functools import cached_property
from io import StringIO
from lxml import html
from pandas import DataFrame, Series
from typing import List, Union
import numpy as np
import pandas as pd
import random, requests, time


class FnGuide:

    def __init__(self, ticker: str):
        self.URL = SCHEMA.URLS(ticker)
        self.ticker = ticker
        return

    @staticmethod
    def _fetch(url: str, encoding: str = "utf-8") -> requests.Response:
        session = requests.Session()

        for attempt in range(5):
            try:
                resp = session.get(url, headers=SCHEMA.HEADER, timeout=(3, 10))
                if resp.status_code == 200:
                    resp.encoding = encoding
                    return resp

                if resp.status_code in (502, 503, 504):
                    time.sleep(3 + random.random() * 5)
                    continue

                if resp.status_code in (403, 429):
                    raise PermissionError(f"Blocked: {resp.status_code}")

            except requests.RequestException:
                time.sleep(3 + random.random() * 5)
        raise ConnectionError(f"Failed to fetch after retries: {url}")

    @staticmethod
    def _statement2numbers(yy: DataFrame, qq: DataFrame) -> Series:

        def __growth(arr: np.ndarray):
            if abs(arr[0]) <= 0.1:
                return np.nan
            if arr[0] < 0 < arr[-1]:
                return 9999.9999  # 흑자 전환
            if arr[0] > 0 > arr[-1]:
                return -9999.9999  # 적자 전환
            if arr[0] < 0 and arr[-1] < 0:
                return -9999.9998  # 적자 지속
            return round(100 * (arr[-1] - arr[0]) / abs(arr[0]), 2)

        def __separate_confirmed_estimated(st: DataFrame):
            """
            잠정 실적(P)이 존재하는 경우 잠정 실적을 확정 실적에 준하여 계산에 사용
            """
            _confirmed = st[~st.index.str.contains(r"\(|\)")].copy()
            _estimated = st[~st.index.isin(_confirmed.index)].copy()
            if _estimated.index[0].endswith('(P)'):
                prov = _estimated.iloc[[0]].copy()  # 최근 잠정 실적
                _confirmed = pd.concat([_confirmed, prov], axis=0)
                _estimated.drop(index=_estimated.index[0], inplace=True)
            return _confirmed, _estimated

        # 확정 실적과 추정/잠정 실적 분리
        confirmed_yy, estimated_yy = __separate_confirmed_estimated(yy)
        confirmed_qq, _ = __separate_confirmed_estimated(qq)
        trailing = confirmed_qq.iloc[-4:].sum()

        # 매출처 이름
        sales_col = confirmed_yy.columns[0]
        fiscal_month = confirmed_yy.index[-1]

        # 영업이익률 계산 일원화
        confirmed_yy['영업이익률'] = round(100 * confirmed_yy['영업이익'] / confirmed_yy[sales_col], 2)
        confirmed_qq['영업이익률'] = round(100 * confirmed_qq['영업이익'] / confirmed_qq[sales_col], 2)
        estimated_yy['영업이익률'] = round(100 * estimated_yy['영업이익'] / estimated_yy[sales_col], 2)

        # 계산용 데이터
        # - 정적 데이터: 확정/잠정 실적 + 추정 실적 1개년
        # - 동적 데이터: 확정/잠정 실적 + 추정 실적 1개년에 대한 변화율
        #   @[{"매출", "이자수익", "보험수익"}, "영업이익", "당기순이익",
        #     "자산총계", "부채총계", "영업이익률", "EPS", "DPS"]
        columns = SCHEMA.KEY_CHANGE_RATE.copy()
        columns.update({sales_col: "sales", "배당성향": "payoutRatio"})

        static = pd.concat([confirmed_yy, estimated_yy.iloc[[0]]])

        # 배당성향 계산
        # - 잠정 실적에 DPS가 존재하는 경우, 직전 확정 실적과 최근 4분기 합산 DPS 중 큰 값으로 대체
        if fiscal_month.endswith('(P)') and not pd.isna(static.at[fiscal_month, 'DPS']):
            static.at[fiscal_month, 'DPS'] \
                = max(static.at[confirmed_yy.index[-2], 'DPS'], trailing['DPS'])
        static['발행주식수'] = static['발행주식수'].ffill()
        static['배당성향'] = round(100 * (1000 * static['발행주식수']) * static['DPS'] / (static['당기순이익'] * 1e+8), 2)

        # 변화율(성장률) 계산
        # - 잠정 실적이 존재하는 경우, 결측치는 직전 확정실적으로 대체
        dynamic_fiscal = static[columns.keys()] \
            .rename(columns=columns) \
            .rolling(2) \
            .apply(__growth, raw=True) \
            .replace({9999.9999: "흑자전환", -9999.9999: "적자전환", -9999.9998: "적자지속"})
        if fiscal_month.endswith('(P)'):
            rebase = static.ffill().copy()
        else:
            rebase = static.copy()
        dynamic_estimated = rebase[columns.keys()] \
            .rename(columns=columns) \
            .rolling(2) \
            .apply(__growth, raw=True) \
            .replace({9999.9999: "흑자전환", -9999.9999: "적자전환", -9999.9998: "적자지속"})
        yoy = confirmed_qq[[c for c in columns if c in confirmed_qq.columns]] \
            .rename(columns=columns) \
            .rolling(5) \
            .apply(__growth, raw=True) \
            .replace({9999.9999: "흑자전환", -9999.9999: "적자전환", -9999.9998: "적자지속"}) \
            .iloc[-1][['sales', 'profit', 'netProfit', 'profitRate', 'eps']]
        yoy.index = [f'yoy{col[0].upper()}{col[1:]}' for col in yoy.index]

        # 최근 4분기 합산 실적 및 최근 결산년도 주요 확정 실적 취합
        # - 최근 결산년도 EPS는 별도 계산
        # - 결측치는 직전 회계년도 실적으로 대체
        fiscal = static.loc[fiscal_month].copy()
        fiscal = fiscal.combine_first(static.loc[confirmed_yy.index[-2]])
        data = Series(data=dict(
            trailingSales=trailing[sales_col],
            trailingProfit=trailing['영업이익'],
            trailingNetProfit=trailing['당기순이익'],
            trailingProfitRate=100 * trailing['영업이익'] / trailing[sales_col] if trailing[sales_col] > 0 else np.nan,
            trailingEps=trailing['EPS'],
            fiscalMonth=fiscal.name,
            fiscalSales=fiscal[sales_col],
            fiscalProfit=fiscal['영업이익'],
            fiscalNetProfit=fiscal['당기순이익'],
            fiscalAsset=fiscal['자산총계'],
            fiscalCapital=fiscal['자본총계'],
            fiscalDebt=fiscal['부채총계'],
            fiscalDebtRatio=fiscal['부채비율'],
            fiscalRetentionRate=fiscal['유보율'],
            fiscalProfitRate=100 * fiscal['영업이익'] / fiscal[sales_col] if fiscal[sales_col] > 0 else np.nan,
            fiscalDps=fiscal['DPS'],
            # fiscalEps=fiscal['EPS'], # 직전 EPS 별도 계산 (중복 방지)
            fiscalDividendYield=fiscal['배당수익률'],
            fiscalPayoutRatio=fiscal['배당성향'],
            returnOnAsset=fiscal['ROA'],
            returnOnEquity=fiscal['ROE'],
        ))
        fiscal_pct = dynamic_fiscal.loc[fiscal_month]
        fiscal_pct = fiscal_pct.combine_first(dynamic_fiscal.loc[confirmed_yy.index[-2]])
        for col in columns.values():
            data[f'fiscal{col[0].upper() + col[1:]}Growth'] = fiscal_pct[col]
        for i, val in yoy.items():
            data[i] = val

        # 최근 추정년도 기준 실적
        data['estimatedMonth'] = est = estimated_yy.index[0]
        estimated = static.loc[est]
        for key, col in columns.items():
            if col == 'eps':
                continue  # @estimation과 중복 방지
            data[f'estimated{col[0].upper() + col[1:]}'] = estimated[key]

        estimated_pct = dynamic_estimated.loc[est]
        for col in columns.values():
            data[f'estimated{col[0].upper() + col[1:]}Growth'] = estimated_pct[col]

        return data

    @staticmethod
    def _typecast(value: str) -> Union[int, float, str]:
        if str(value) in ['', ' ', '-', 'nan', '완전잠식']:
            return np.nan

        value = str(value) \
                .replace(" ", "") \
                .replace("%", "") \
                .replace(",", "") \
                .replace("N/A(IFRS)", "")
        if any([c in value for c in ['/', '*']]) or all([c.isalpha() for c in value]):
            return value
        value = value.lower()
        if not any([char.isdigit() for char in value]):
            return np.nan
        return float(value) if "." in value or "-" in value else int(value)

    def _src2statement(self, src: DataFrame) -> DataFrame:
        data = src.set_index(keys=[src.columns[0]])
        if isinstance(data.columns[0], tuple):
            data.columns = data.columns.droplevel()
        else:
            data.columns = data.iloc[0]
            data = data.drop(index=data.index[0])
        data = data.T
        data.index.name = '기말'
        data.index = [
            idx.replace("(E) : Estimate 컨센서스, 추정치 ", "").replace("(P) : Provisional 잠정실적 ", "")
            for idx in data.index
        ]
        data.columns.name = None
        data = data.map(self._typecast) \
            .drop(columns=[col for col in data.columns if "발표기준" in col]) \
            .rename(columns={col: col[:col.find("(")] if "(" in col else col for col in data.columns})
        return data

    @cached_property
    def _snapshot_text(self) -> str:
        return self._fetch(self.URL.SNAPSHOT).text

    @cached_property
    def _snapshot_tables(self) -> List[DataFrame]:
        return pd.read_html(StringIO(self._snapshot_text), header=0, displayed_only=False)

    @property
    def annual_statement(self) -> DataFrame:
        return self.annual_statement_consolidate if self.gb == 'D' else self.annual_statement_separate

    @cached_property
    def annual_statement_consolidate(self) -> DataFrame:
        if len(self._snapshot_tables) == 17:
            n = 11
        elif len(self._snapshot_tables) == 15:
            n = 9
        else:
            raise IndexError(f"Unexpected number of snapshot tables for {self.ticker}")
        return self._src2statement(self._snapshot_tables[n])

    @cached_property
    def annual_statement_separate(self) -> DataFrame:
        if len(self._snapshot_tables) == 17:
            n = 14
        elif len(self._snapshot_tables) == 15:
            n = 12
        else:
            raise IndexError(f"Unexpected number of snapshot tables for {self.ticker}")
        return self._src2statement(self._snapshot_tables[n])

    @cached_property
    def date(self) -> str:
        return html.fromstring(self._snapshot_text).xpath('//span[@class="date"]//text()')[0][1:-1]

    @cached_property
    def estimation(self) -> Series:
        if len(self._snapshot_tables) == 17:
            n = 7
        elif len(self._snapshot_tables) == 15:
            n = 5
        else:
            raise IndexError(f"Unexpected number of snapshot tables for {self.ticker}")
        data = self._snapshot_tables[n].rename(columns=SCHEMA.LABEL_ESTIMATION).T[0]
        return data.map(self._typecast)

    @cached_property
    def gb(self) -> str:
        sy = self.annual_statement_separate
        cy = self.annual_statement_consolidate
        sq = self.quarter_statement_separate
        cq = self.quarter_statement_consolidate
        if (sy.count().sum() > cy.count().sum()) or (sq.count().sum() > cq.count().sum()):
            return 'B'  # 별도
        else:
            return 'D'  # 연결

    @property
    def quarter_statement(self) -> DataFrame:
        return self.quarter_statement_consolidate if self.gb == 'D' else self.quarter_statement_separate

    @cached_property
    def quarter_statement_consolidate(self) -> DataFrame:
        if len(self._snapshot_tables) == 17:
            n = 12
        elif len(self._snapshot_tables) == 15:
            n = 10
        else:
            raise IndexError(f"Unexpected number of snapshot tables for {self.ticker}")
        return self._src2statement(self._snapshot_tables[n])

    @cached_property
    def quarter_statement_separate(self) -> DataFrame:
        if len(self._snapshot_tables) == 17:
            n = 15
        elif len(self._snapshot_tables) == 15:
            n = 13
        else:
            raise IndexError(f"Unexpected number of snapshot tables for {self.ticker}")
        return self._src2statement(self._snapshot_tables[n])

    @cached_property
    def numbers(self) -> Series:
        table = self._snapshot_tables[0]
        fifty_two_weeks = table.iloc[0, 1].replace(' ', '').split("/")
        shares_outstanding = table.iloc[5, 1].replace(' ', '').split('/')
        float_shares = table.iloc[6, 1].replace(' ', '').split('/')

        data = Series(data=dict(
            numbersDate=self.date,
            close=table.columns[1].replace(' ', '').split("/")[0],
            fiftyTwoWeekHigh=fifty_two_weeks[0],
            fiftyTwoWeekLow=fifty_two_weeks[1],
            foreignRate=table.iloc[1, 3],
            beta=table.iloc[2, 3],
            sharesOutstanding=shares_outstanding[0],
            sharesPreferred=shares_outstanding[1],
            sharesFloating=float_shares[0],
            sharesFloatingRate=float_shares[1],
            ifrsType=self.gb if not self.ticker in SCHEMA.NUMBER_EXCEPTION else np.nan,
        ))

        tree = html.fromstring(self._snapshot_text)
        for dl in tree.xpath('//div[@id="corp_group2"]/dl'):
            key = "".join(dl.xpath('.//a[contains(@class, "tip_in")]//text()')).strip()
            if key == "PER":
                data['fiscalPe'] = dl.xpath('./dd/text()')[0].strip()
            if key == "12M PER":
                data['fowardPe'] = dl.xpath('./dd/text()')[0].strip()
            if key == "업종 PER":
                data['industryPe'] = dl.xpath('./dd/text()')[0].strip()
            if key == "PBR":
                data['fiscalPriceToBook'] = dl.xpath('./dd/text()')[0].strip()
        data = data.map(self._typecast)

        if data.fiscalPe > 0:
            data['fiscalEps'] = round(data.close / data.fiscalPe, 2)
        data['forwardEps'] = round(data.close / data.fowardPe, 2) if data.fowardPe > 0 else np.nan
        if not self.ticker in SCHEMA.NUMBER_EXCEPTION:
            data = pd.concat([
                data,
                self.estimation,
                self._statement2numbers(self.annual_statement, self.quarter_statement)
            ])
        data.name = self.ticker
        if not data.index.is_unique:
            data = data.sort_values(na_position='last') \
                .groupby(level=0) \
                .head(1)
        return data


if __name__ == "__main__":
    fng = FnGuide('000660')
    # fng.annual_statement
    # fng.quarterly_statement
    # fng.snapshot
    # fng.per_band
    # fng.foreign_rate
    # fng.products
    # fng.expenses
