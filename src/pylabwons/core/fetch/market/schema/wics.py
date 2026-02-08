from pylabwons.schema.datadict import DataDictionary
from typing import Dict


CODES:Dict[str, str] = {
    'WI100': '에너지', 'WI110': '화학',
    'WI200': '비철금속', 'WI210': '철강', 'WI220': '건설', 'WI230': '기계', 'WI240': '조선', 'WI250': '상사,자본재', 'WI260': '운송',
    'WI300': '자동차', 'WI310': '화장품,의류', 'WI320': '호텔,레저', 'WI330': '미디어,교육', 'WI340': '소매(유통)',
    'WI400': '필수소비재', 'WI410': '건강관리',
    'WI500': '은행', 'WI510': '증권', 'WI520': '보험',
    'WI600': '소프트웨어', 'WI610': 'IT하드웨어', 'WI620': '반도체', 'WI630': 'IT가전', 'WI640': '디스플레이',
    'WI700': '통신서비스',
    'WI800': '유틸리티'
}

EXCEPTIONS = {
    '950160': {
        "name": "코오롱티슈진",
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    },
    '950210': {
        'name': '프레스티지바이오파마',
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    },
    '009410': {
        'name': '태영건설',
        "industryCode": "WI220",
        "industryName": "건설",
        "sectorCode": "G20",
        "sectorName": "산업재"
    },
    '052020': {
        'name': '에스티큐브',
        "industryCode": "WI410",
        "industryName": "건강관리",
        "sectorCode": "G35",
        "sectorName": "건강관리"
    }
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://comp.fnguide.com/",
    "Connection": "keep-alive",
}

LABELS:Dict[str, str] = {
    'CMP_CD': 'ticker', 'CMP_KOR': 'name',
    'SEC_CD': 'sectorCode', 'SEC_NM_KOR': 'sectorName',
    'IDX_CD': 'industryCode', 'IDX_NM_KOR': 'industryName',
}

REITS:Dict[str, str] = {
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

SRC = "https://raw.githubusercontent.com/labwons/pylabwons/refs/heads/main/src/pylabwons/archive/wics.json"

URL = DataDictionary(
    BASE='https://www.wiseindex.com/Index/Index#/G1010.0.Components',
    SECTOR=lambda date, code: f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={date}&sec_cd={code}'
)


if __name__ == '__main__':
    print(URL)