from pylabwons.core.fetch.stock import schema as SCHEMA
from functools import cached_property
from pandas import DataFrame, Series
from typing import Dict, Union
from xml.etree.ElementTree import Element, ParseError, fromstring
import numpy as np
import pandas as pd
import random, requests, re, time


class FnGuide:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self._URLS = SCHEMA.URLS(ticker)
        return

    @staticmethod
    def type_cast(value: str) -> Union[int, float, str]:
        value = str(value)
        if any([c in value for c in ['/', '*']]):
            return value
        if str(value) == 'nan':
            return np.nan
        value = value.lower().replace(",", "")
        if not any([char.isdigit() for char in value]):
            return np.nan
        return float(value) if "." in value or "-" in value else int(value)

    @staticmethod
    def fetch(url: str, encoding: str = "euc-kr") -> requests.Response:
        session = requests.Session()

        for attempt in range(5):
            try:
                resp = session.get(
                    url,
                    headers=SCHEMA.HEADER,
                    timeout=(3, 10)
                )

                if resp.status_code == 200:
                    resp.encoding = encoding
                    return resp

                # 502/503은 서버 문제 → backoff
                if resp.status_code in (502, 503, 504):
                    time.sleep(3 + random.random() * 5)
                    continue

                # 403/429면 사실상 차단
                if resp.status_code in (403, 429):
                    raise PermissionError(f"Blocked: {resp.status_code}")

            except requests.RequestException:
                time.sleep(3 + random.random() * 5)

        raise ConnectionError(f"Failed to fetch after retries: {url}")

    def _statement(self, tag: str) -> DataFrame:
        try:
            obj = self.xml.find(tag)
        except (ConnectionError, ParseError):
            return DataFrame()
        if obj is None:
            return DataFrame()
        columns = [val.text.replace(" ", "") for val in obj.findall('field')]
        selector = [col for col in columns if not col in SCHEMA.STATEMENT_EXCLUDE]
        index, data = [], []
        for record in obj.findall('record'):
            index.append(record.find('date').text)
            data.append([val.text for val in record.findall('value')])
        return DataFrame(index=index, columns=columns, data=data)[selector].map(self.type_cast)

    @cached_property
    def _expenses(self) -> Dict[str, DataFrame]:
        json = self.fetch(self._URLS.EXPENSES, encoding='utf-8').json()

        def _get_(period: str) -> DataFrame:
            manage = DataFrame(json[f"05_{period}"]).set_index(keys="GS_YM")["VAL1"]
            cost = DataFrame(json[f"06_{period}"]).set_index(keys="GS_YM")["VAL1"]
            manage.index.name = cost.index.name = '기말'
            data = pd.concat({"판관비율": manage, "매출원가율": cost}, axis=1)
            for col in data:
                data[col] = data[col].apply(self.type_cast)
            if period == "Q":
                data.index = [
                    c.replace("03", "1Q").replace("06", "2Q").replace("09", "3Q").replace("12", "4Q") for c in
                    data.index
                ]
            return data

        return dict(Y=_get_('Y'), Q=_get_('Q'))

    @cached_property
    def _multiple_bands(self) -> Dict[str, DataFrame]:
        resp = self.fetch(self._URLS.BANDS, encoding='utf-8')
        json = resp.json()

        def _get_(key: str) -> DataFrame:
            head = DataFrame(json[key])[['ID', 'NAME']].set_index(keys='ID')
            head = head.to_dict()['NAME']
            head.update({'GS_YM': '날짜', 'PRICE': '종가'})
            data = DataFrame(json['CHART']).rename(columns=head)[head.values()]
            data["날짜"] = pd.to_datetime(data["날짜"])
            data = data.set_index(keys='날짜')
            if "0.00X" in data.columns:
                data = data.drop(columns=['0.00X'])
            data = data.dropna(how='all', axis=1)
            for col in data:
                data[col] = data[col].apply(self.type_cast)
            return data

        return {'PER': _get_('CHART_E'), 'PBR': _get_('CHART_B')}

    @cached_property
    def gb(self) -> str:
        sy = self._statement('financial_highlight_ifrs_B/financial_highlight_annual')
        cy = self._statement('financial_highlight_ifrs_D/financial_highlight_annual')
        sq = self._statement('financial_highlight_ifrs_B/financial_highlight_quarter')
        cq = self._statement('financial_highlight_ifrs_D/financial_highlight_quarter')
        if (sy.count().sum() > cy.count().sum()) or (sq.count().sum() > cq.count().sum()):
            return 'B'  # 별도
        else:
            return 'D'  # 연결

    @property
    def annual_expense(self) -> DataFrame:
        return self._expenses['Y']

    @cached_property
    def annual_statement(self) -> DataFrame:
        return self._statement(f'financial_highlight_ifrs_{self.gb}/financial_highlight_annual')

    @cached_property
    def foreign_rate(self) -> DataFrame:
        cols = {'TRD_DT': 'date', 'J_PRC': 'close', 'FRG_RT': 'rate'}
        objs = {}
        for _url in self._URLS.FOREIGNRATE3M, self._URLS.FOREIGNRATE1Y, self._URLS.FOREIGNRATE3Y:
            resp = self.fetch(_url, encoding='utf-8')
            data = DataFrame(resp.json()['CHART'])[cols.keys()]
            data = data.rename(columns=cols).set_index(keys='date')
            data.index = pd.to_datetime(data.index)
            for col in data:
                data[col] = data[col].apply(self.type_cast)
            objs[_url[_url.rfind('_') + 1: _url.rfind('.')]] = data
        return pd.concat(objs=objs, axis=1)

    @property
    def pbr_band(self) -> DataFrame:
        return self._multiple_bands['PBR']

    @property
    def per_band(self) -> DataFrame:
        return self._multiple_bands['PER']

    @cached_property
    def products(self) -> DataFrame:
        json = self.fetch(self._URLS.PRODUCTS, encoding='utf-8').json()
        head = DataFrame(json['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
        head.update({'PRODUCT_DATE': '기말'})
        values = list(head.values())
        for n, (key, value) in enumerate(head.items()):
            if value in values[:n]:
                head[key] = f'{value}_Copy'
        data = DataFrame(json['chart']).rename(columns=head).set_index(keys='기말')
        data = data.drop(columns=[c for c in data.columns if data[c].astype(float).sum() == 0])

        i = data.columns[-1]
        data['Sum'] = data.astype(float).sum(axis=1)
        data = data[(90 <= data.Sum) & (data.Sum < 110)].astype(float)
        data[i] = data[i] - (data.Sum - 100)
        return data.drop(columns=['Sum'])

    @property
    def quarterly_expense(self) -> DataFrame:
        return self._expenses['Q']

    @cached_property
    def quarterly_statement(self) -> DataFrame:
        data = self._statement(f'financial_highlight_ifrs_{self.gb}/financial_highlight_quarter')
        data.index = [
            c.replace("03", "1Q").replace("06", "2Q").replace("09", "3Q").replace("12", "4Q") for c in data.index
        ]
        return data

    @cached_property
    def snapshot(self) -> Series:
        obj = {child.tag: child.text for child in self.xml.find('price')}
        if self.xml.find('consensus') is not None:
            obj.update({child.tag: child.text for child in self.xml.find('consensus')})
        return Series(obj, name=self.ticker).apply(self.type_cast)

    @cached_property
    def xml(self) -> Element:
        resp = self.fetch(self._URLS.XML)
        text = resp.text.replace("<![CDATA[", "").replace("]]>", "")
        text = re.sub(r'<business_summary>.*?</business_summary>', '', text, flags=re.DOTALL)
        return fromstring(text)

if __name__ == "__main__":
    fng = FnGuide('000660')
    # fng.annual_statement
    # fng.quarterly_statement
    # fng.snapshot
    # fng.per_band
    # fng.foreign_rate
    # fng.products
    fng.expenses
