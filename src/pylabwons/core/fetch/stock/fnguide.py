from pylabwons.core.fetch.stock import schema as SCHEMA
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
            if arr[0] < 0 < arr[1]:
                return 9999.9999
            if arr[0] > 0 > arr[1]:
                return -9999.9999
            if arr[0] < 0 and arr[1] < 0:
                return -9999.9998
            return round(100 * (arr[1] - arr[0]) / abs(arr[0]), 2)

        # 확정 실적과 추정/잠정 실적 분리
        st = yy.copy()
        confirmed = st[~st.index.str.contains(r"\(|\)")].copy()
        estimated = st[~st.index.isin(confirmed.index)].copy()
        fiscal_year = confirmed.index[-1]

        # 분기 실적의 경우 같은 연도로 시작하는 실적이 4개인 경우 추출
        qq = qq.copy()
        mask = qq.groupby(qq.index.str[:4]).count().max(axis=1)
        year = mask[mask == 4]
        if not year.empty:
            qq = qq[qq.index.str.startswith(year.index[0])]

        # 잠정 실적이 존재하는 경우 잠정 실적을 확정 실적에 준하여 계산에 사용
        # 잠정 실적 중 결측치는 이전 결산년도로 채움
        if estimated.index[0].endswith('(P)'):
            fiscal_year = estimated.index[0]
            prov = estimated.iloc[[0]].copy()
            prev = confirmed.iloc[[-1]].copy()
            prov.index = prev.index = [0]
            prov = prov.combine_first(prev)
            prov.index = [estimated.index[0]]
            prov['DPS'] = qq['DPS'].sum()
            confirmed = pd.concat([confirmed, prov], axis=0)
            estimated.drop(index=estimated.index[0], inplace=True)

        # 3분기 실적이 발표되고 해가 바뀐 경우
        # 3개 분기 합산의 연장 값을 계산 값으로 활용
        # TODO
        else:
            qq = qq[~qq.index.str.contains(r"\(|\)")].copy()
            # if (len(qq) >= 3):

            pass

        # 최근 확정 실적 2개년과 추정 실적 1개년을 병합
        base = pd.concat([confirmed.iloc[-2:], estimated.iloc[[0]]])
        base['발행주식수'] = base['발행주식수'].ffill()
        base['배당성향'] = round(100 * (1000 * base['발행주식수']) * base['DPS'] / (base['당기순이익'] * 1e+8), 2)

        # 최근 결산년도 주요 확정 실적 취합
        fiscal:Series = base.loc[fiscal_year]
        data = Series(data=dict(
            fiscalYear=fiscal_year,
            sales=fiscal[base.columns[0]],
            profit=fiscal['영업이익'],
            netProfit=fiscal['당기순이익'],
            asset=fiscal['자산총계'],
            capital=fiscal['자본총계'],
            debt=fiscal['부채총계'],
            debtRatio=fiscal['부채비율'],
            retentionRate=fiscal['유보율'],
            profitRate=fiscal['영업이익률'],
            returnOnAsset=fiscal['ROA'],
            returnOnEquity=fiscal['ROE'],
            dps=fiscal['DPS'],
            payoutRatio=fiscal['배당성향'],
            dividendYield=fiscal['배당수익률']
        ))

        # @base에 대한 실적 증감율 계산
        rename = SCHEMA.KEY_CHANGE_RATE.copy()
        rename.update({base.columns[0]: "sales", "배당성향": "payoutRatio"})
        rebase = base[[base.columns[0]] + list(SCHEMA.KEY_CHANGE_RATE.keys()) + ['배당성향']]
        rebase = rebase.rename(columns=rename)
        rated = rebase.rolling(2).apply(__growth, raw=True).iloc[1:]
        rated = rated.replace({9999.9999: "흑자전환", -9999.9999: "적자전환", -9999.9998: "적자지속"})

        # 최근 결산년도 주요 증감률 취합
        fiscal_pct = rated.iloc[0]
        fiscal_pct.index = [f'{n}Growth' for n in fiscal_pct.index]
        data = pd.concat([data, fiscal_pct])

        # 최근 추정년도 기준 추정 증감률 취합
        data['estimateYear'] = estimate_year = estimated.index[0]
        estimated = rebase.loc[estimate_year]
        estimated.index = [f'estimate{n.capitalize()}' for n in estimated.index]
        estimated_pct = rated.iloc[1]
        estimated_pct.index = [f'estimate{n.capitalize()}Growth' for n in estimated_pct.index]
        data = pd.concat([data, estimated, estimated_pct])
        return data

    @staticmethod
    def _typecast(value: str) -> Union[int, float, str]:
        value = str(value)
        if value in ['-', 'nan']:
            return np.nan
        if any([c in value for c in ['/', '*']]) or all([c.isalpha() for c in value]):
            return value
        value = value.lower().replace(",", "")
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
        data = data.map(self._typecast)
        data = data.drop(columns=[col for col in data.columns if "발표기준" in col])
        data = data.rename(columns={col: col[:col.find("(")] if "(" in col else col for col in data.columns})
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
        return self._src2statement(self._snapshot_tables[11])

    @cached_property
    def annual_statement_separate(self) -> DataFrame:
        return self._src2statement(self._snapshot_tables[14])

    @cached_property
    def date(self) -> str:
        return html.fromstring(self._snapshot_text).xpath('//span[@class="date"]//text()')[0][1:-1]

    @cached_property
    def estimation(self) -> Series:
        data = self._snapshot_tables[7].rename(columns=SCHEMA.LABEL_ESTIMATION).T[0]
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
        return self._src2statement(self._snapshot_tables[12])

    @cached_property
    def quarter_statement_separate(self) -> DataFrame:
        return self._src2statement(self._snapshot_tables[15])

    @cached_property
    def numbers(self) -> Series:
        table = self._snapshot_tables[0]
        fifty_two_weeks = table.iloc[0, 1].replace(' ', '').split("/")
        shares_outstanding = table.iloc[5, 1].replace(' ', '').split('/')
        float_shares = table.iloc[6, 1].replace(' ', '').split('/')

        data = Series(name=self.ticker)
        data['ticker'] = str(self.ticker)
        data['date'] = self.date
        data['close'] = table.columns[1].replace(' ', '').split("/")[0]
        data['fiftyTwoWeekHigh'] = fifty_two_weeks[0]
        data['fiftyTwoWeekLow'] = fifty_two_weeks[1]
        data['foreignRate'] = table.iloc[1, 3]
        data['beta'] = table.iloc[2, 3]
        data['sharesOutstanding'] = shares_outstanding[0]
        data['sharesPreferred'] = shares_outstanding[1]
        data['sharesFloating'] = float_shares[0]
        data['sharesFloatingRate'] = float_shares[1]
        data['ifrsType'] = self.gb

        tree = html.fromstring(self._snapshot_text)
        for dl in tree.xpath('//div[@id="corp_group2"]/dl'):
            key = "".join(dl.xpath('.//a[contains(@class, "tip_in")]//text()')).strip()
            if key == "PER":
                data['fiscalPE'] = dl.xpath('./dd/text()')[0].strip()
            if key == "12M PER":
                data['fowardPE'] = dl.xpath('./dd/text()')[0].strip()
            if key == "업종 PER":
                data['industryPE'] = dl.xpath('./dd/text()')[0].strip()
            if key == "PBR":
                data['fiscalPriceToBook'] = dl.xpath('./dd/text()')[0].strip()

        data = data.map(self._typecast)
        data['fiscalEps'] = round(data.close / data.fiscalPE, 2) if data.fiscalPE > 0 else np.nan
        data['forwardEps'] = round(data.close / data.fowardPE, 2) if data.fowardPE > 0 else np.nan
        data = pd.concat(
            [data, self.estimation, self._statement2numbers(self.annual_statement, self.quarter_statement)])
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
