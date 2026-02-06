from pylabwons.schema.datadict import DataDictionary


URLS = lambda ticker: DataDictionary(
    BANDS=f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{ticker}_D.json",
    FOREIGNRATE3M=f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_3M.json",
    FOREIGNRATE1Y=f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_1Y.json",
    FOREIGNRATE3Y=f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_3Y.json",
    PRODUCTS=f"http://cdn.fnguide.com/SVO2/json/chart/02/chart_A{ticker}_01_N.json",
    EXPENSES=f"http://cdn.fnguide.com/SVO2/json/chart/02/chart_A{ticker}_D.json",
    XML=f"http://cdn.fnguide.com/SVO2/xml/Snapshot_all/{ticker}.xml"
)

STATEMENT_EXCLUDE = [
    '영업이익(발표기준)', '자본금(억원)',
    '지배주주순이익(억원)', '비지배주주순이익(억원)', '순이익률(%)',
    '지배주주지분(억원)', '비지배주주지분(억원)', '지배주주순이익률(%)',
    '발행주식수(천주)',
]

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com"
}