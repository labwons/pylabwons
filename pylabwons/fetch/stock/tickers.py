from pylabwons.util.tradingdate import TradingDate

from io import StringIO
from pandas import DataFrame
from pykrx.stock import (
    get_exhaustion_rates_of_foreign_investment,
    get_market_cap_by_ticker,
    get_market_ohlcv_by_ticker
)
from time import sleep
from typing import Dict
import pandas as pd
import requests


RENAMER = {
    "회사명":"name", 
    "시장구분":"market", 
    "종목코드":"ticker", 
    "업종":"KRXIndustry",
    "주요제품":"products", 
    "상장일":"IPO",
    '시가': 'open',
    '고가': 'high',
    '저가': 'low',
    '종가': 'close',
    '등락률': 'changeRate',
    '시가총액': 'marketCap',
    '거래량': 'volume',
    '거래대금': 'amount',
    '상장주식수':'shares',
    '보유수량': 'foreignersShares',
    '지분율': 'foreignersRate',
    '한도수량': 'exhaustionShares',
    '한도소진률': 'exhsuationRate'
}


def get_corporations() -> DataFrame:
    try:
        html = requests.get('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download').text
        corp = pd.read_html(io=StringIO(html), encoding='euc-kr')[0]
        corp['종목코드'] = corp['종목코드'].astype(str).str.zfill(6)
        corp = corp.drop(columns=['대표자명', '홈페이지', '지역', '결산월'])
        corp = corp.rename(columns={key:val for key, val in RENAMER.items() if key in corp})
        corp['market'] = corp['market'].str.replace("코스닥", "KOSDAQ").replace("유가","KOSPI").replace("코넥스", "KONEX")
        corp = corp.set_index(keys='ticker')        
        return corp
    except (KeyError, Exception):
        return DataFrame()

def get_ohlcvs(date:str='') -> DataFrame:
    if not date:
        date = TradingDate.recent
    try:
        data = get_market_ohlcv_by_ticker(date=date, market='ALL')
        data = data.drop(columns=['등락률'])
        data.index.name = 'ticker'
        data = data.rename(columns={key:val for key, val in RENAMER.items() if key in data})
        return data
    except (KeyError, Exception):
        return DataFrame()

def get_market_caps(date:str='') -> DataFrame:
    if not date:
        date = TradingDate.recent
    try:
        data = get_market_cap_by_ticker(date=date, market='ALL')
        data.index.name = 'ticker'
        data = data.rename(columns={key:val for key, val in RENAMER.items() if key in data})
        return data
    except (KeyError, Exception):
        return DataFrame()

def get_foreigner_rates(date:str='') -> DataFrame:
    if not date:
        date = TradingDate.recent
    try:
        data = get_exhaustion_rates_of_foreign_investment(date=date, market='ALL')
        data.index.name = 'ticker'
        data = data.rename(columns={key:val for key, val in RENAMER.items() if key in data})
        typecastInt32 = ['shares', 'foreignersShares', 'exhaustionShares']
        typecastFloat = ['foreignersRate', 'exhsuationRate']
        data[typecastInt32] = data[typecastInt32].astype('int32')
        data[typecastFloat] = data[typecastFloat].astype('float32')
        return data
    except (KeyError, Exception):
        return DataFrame()


def get_sectors(date:str='', logger=None) -> DataFrame:

    SECTOR_CODE:Dict[str, str] = {
        'WI100': '에너지', 
        'WI110': '화학',
        'WI200': '비철금속', 
        'WI210': '철강', 
        'WI220': '건설', 
        'WI230': '기계', 
        'WI240': '조선', 
        'WI250': '상사,자본재', 
        'WI260': '운송',
        'WI300': '자동차', 
        'WI310': '화장품,의류', 
        'WI320': '호텔,레저', 
        'WI330': '미디어,교육', 
        'WI340': '소매(유통)',
        'WI400': '필수소비재', 
        'WI410': '건강관리',
        'WI500': '은행', 
        'WI510': '증권', 
        'WI520': '보험',
        'WI600': '소프트웨어', 
        'WI610': 'IT하드웨어', 
        'WI620': '반도체', 
        'WI630': 'IT가전', 
        'WI640': '디스플레이',
        'WI700': '통신서비스',
        'WI800': '유틸리티'
    }

    CODE_LABEL:Dict[str, str] = {
        'CMP_CD': 'ticker', 
        'CMP_KOR': 'name',
        'SEC_CD': 'sectorCode', 
        'SEC_NM_KOR': 'sectorName',
        'IDX_CD': 'industryCode', 
        'IDX_NM_KOR': 'industryName',
    }

    def _get_sector(code:str, date:str, retry:int=5) -> DataFrame:
        try:
            resp = requests.get(url=f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}')
        except (Exception, TypeError):
            return DataFrame()

        if "hmg_corp" in resp.text:
            return DataFrame()
        
        if not resp.status_code == 200:
            if not retry:
                return DataFrame()
            else:
                sleep(5)
                return _get_sector(code, date, retry-1)

        return DataFrame(resp.json()['list'])
        
    date = date if date else TradingDate.wise
    if not date:
        if logger: logger.error('- FAILED TO FETCH [SECTOR COMPOSITION]')
        return DataFrame()

    objs, size = [], len(SECTOR_CODE)
    for n, (code, name) in enumerate(SECTOR_CODE.items()):
        sector = _get_sector(code, date)
        if sector.empty:
            if logger: logger.error(f'- FAILED TO FETCH ({str(n + 1).zfill(2)}/{size}): {code} {name}')
            return DataFrame()
        else:
            if logger: logger.info(f"- SUCCEED IN FETCHING ({str(n + 1).zfill(2)}/{size}): {code} {name}")
            objs.append(sector)

    data = pd.concat(objs, axis=0, ignore_index=True)

    data.drop(inplace=True, columns=[key for key in data if not key in CODE_LABEL])
    data.drop(inplace=True, index=data[data['SEC_CD'].isna()].index)
    data.rename(inplace=True, columns=CODE_LABEL)
    data.set_index(inplace=True, keys="ticker")
    data['industryName'] = data['industryName'].str.replace("WI26 ", "")

    sc_mdi = data[(data['industryCode'] == 'WI330') & (data['sectorCode'] == 'G50')].index
    sc_edu = data[(data['industryCode'] == 'WI330') & (data['sectorCode'] == 'G25')].index
    sc_sw = data[(data['industryCode'] == 'WI600') & (data['sectorCode'] == 'G50')].index
    sc_it = data[(data['industryCode'] == 'WI600') & (data['sectorCode'] == 'G45')].index
    data.loc[sc_mdi, 'industryCode'], data.loc[sc_mdi, 'industryName'] = 'WI331', '미디어'
    data.loc[sc_edu, 'industryCode'], data.loc[sc_edu, 'industryName'] = 'WI332', '교육'
    data.loc[sc_sw, 'industryCode'], data.loc[sc_sw, 'industryName'] = 'WI601', '소프트웨어'
    data.loc[sc_it, 'industryCode'], data.loc[sc_it, 'industryName'] = 'WI602', 'IT서비스'
    # data['date'] = date
    return data
