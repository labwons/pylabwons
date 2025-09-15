from pylabwons.util.tradingdate import DATETIME

from io import StringIO
from pandas import DataFrame
from pykrx.stock import get_market_cap_by_ticker, get_exhaustion_rates_of_foreign_investment
from time import sleep, perf_counter
from typing import Dict
import pandas as pd
import requests


def get_corporations() -> DataFrame:
    try:
        html = requests.get('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download').text
        corp = pd.read_html(io=StringIO(html), encoding='euc-kr')[0]
        corp['종목코드'] = corp['종목코드'].astype(str).str.zfill(6)
        corp = corp.drop(columns=['대표자명', '홈페이지', '지역', '결산월'])
        corp = corp.rename(columns={
            "회사명":"name", 
            "시장구분":"market", 
            "종목코드":"ticker", 
            "업종":"KRXIndustry",
            "주요제품":"products", 
            "상장일":"IPO"
        })
        corp['market'] = corp['market'].str.replace("코스닥", "KOSDAQ").replace("유가","KOSPI").replace("코넥스", "KONEX")
        corp = corp.set_index(keys='ticker')        
        return corp
    except (KeyError, Exception):
        return DataFrame()


def get_market_caps(date:str='') -> DataFrame:
    if not date:
        date = DATETIME.TRADING
    try:
        caps = get_market_cap_by_ticker(date=date, market='ALL')
        caps.index.name = 'ticker'
        caps = caps.rename(columns={
            '종가':'close',
            '시가총액':'marketCap',
            '거래량':'volume',
            '거래대금':'amount',
            '상장주식수':'shares'
        })
        return caps
    except (KeyError, Exception):
        return DataFrame()


def get_foreigner_rate(date:str='') -> DataFrame:
    if not date:
        date = DATETIME.TRADING
    try:
        data = get_exhaustion_rates_of_foreign_investment(date=date, market='ALL')
        data.index.name = 'ticker'
        data = data.rename(columns={
            '상장주식수':'shares',
            '보유수량': 'foreignersShares',
            '지분율': 'foreignersRate',
            '한도수량': 'exhaustionShares',
            '한도소진률': 'exhsuationRate'
        })
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

    REITS_CODE:Dict[str, str] = {
        "088980": "맥쿼리인프라",
        "395400": "SK리츠",
        "365550": "ESR켄달스퀘어리츠",
        "330590": "롯데리츠",
        "348950": "제이알글로벌리츠",
        "293940": "신한알파리츠",
        "432320": "KB스타리츠",
        "094800": "맵스리얼티1",
        "357120": "코람코라이프인프라리츠",
        "448730": "삼성FN리츠",
        "451800": "한화리츠",
        "088260": "이리츠코크렙",
        "334890": "이지스밸류리츠",
        "377190": "디앤디플랫폼리츠",
        "404990": "신한서부티엔디리츠",
        "417310": "코람코더원리츠",
        "400760": "NH올원리츠",
        "350520": "이지스레지던스리츠",
        "415640": "KB발해인프라",
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
        
    date = date if date else DATETIME.WISE
    if not date:
        if logger: logger.error('- FAILED TO FETCH [SECTOR COMPOSITION]')
        return DataFrame()
    else:
        if logger: logger.info(f'- RESOURCE DATE: {date}')

    objs, size = [], len(SECTOR_CODE) + 1
    for n, (code, name) in enumerate(SECTOR_CODE.items()):
        if logger: logger.info(f"- SUCCEED IN FETCHING ({str(n + 1).zfill(2)}/{size}): {code} {name}")
        sector = _get_sector(code, date)
        if sector.empty:
            if logger: logger.error(f'- FAILED TO FETCH ({str(n + 1).zfill(2)}/{size}): {code} {name}')
            return DataFrame()
        objs.append(sector)

    reits = DataFrame(data={'CMP_KOR': REITS_CODE.values(), 'CMP_CD': REITS_CODE.keys()})
    reits[['SEC_CD', 'IDX_CD', 'SEC_NM_KOR', 'IDX_NM_KOR']] = ['G99', 'WI999', '리츠', '리츠']
    objs.append(reits)
    if logger: logger.info(f"- SUCCEED IN FETCHING ({size}/{size}): WI999 리츠")

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
    data['date'] = date
    return data
