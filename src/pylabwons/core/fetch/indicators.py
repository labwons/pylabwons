from bs4 import BeautifulSoup
from datetime import datetime
from pandas import DataFrame
import requests, time
import pandas as pd

def baker_hughes_rig_count(*years, **kwargs) -> DataFrame:
    """
    연도별 Baker Hughes 미국 리그 카운트 데이터를 크롤링합니다.
    출처: American Oil & Gas Reporter(AOGR)

    Args:
        *years (int): 크롤링할 연도 목록 (지정하지 않으면 현재 연도 기준 과거 12년 치 자동 설정)
        **kwargs: requests.get() 메소드에 전달할 추가 인자 (예: verify=False)

    Returns:
        DataFrame: 날짜(DatetimeIndex)를 인덱스로 가지고, 지역/유형별 리그 카운트를 정수형(int) 컬럼으로 갖는 데이터프레임
    """
    # 1. 크롤링 대상 연도 기본값 설정
    if not years:
        years = [datetime.now().year + n for n in range(-12, 1)]

    objs = []
    # 2. 연도별 데이터 수집 루프
    for year in years:
        # HTTP GET 요청 전송
        response = requests.get(
            url=f"https://www.aogr.com/web-exclusives/us-rig-count/{year}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 "
                              "Safari/537.36"
            },
            timeout=15,
            verify=kwargs.get('verify', True)
        )
        # 응답 실패 시 해당 연도 건너뛰기
        if response.status_code != 200:
            continue

        # HTML 파싱 및 데이터 행(Row) 추출
        soup = BeautifulSoup(response.content, "html.parser")
        divs = soup.find_all("div", class_="p-4 sm:table-row")

        data = []
        # 3. 행별 텍스트 데이터 파싱 루프
        for div in divs:
            parts = list(div.stripped_strings)

            # 첫 번째 요소에서 날짜 추출 (날짜 형식이 아니면 행 건너뛰기)
            try:
                date = datetime.strptime(parts[0], "%m/%d/%Y").date()
            except (TypeError, ValueError, Exception):
                continue

            obj = {'date': date}
            key = []
            # 텍스트 구조를 분석하여 Key(항목명)와 Value(수치) 매핑
            for part in parts[1:]:
                if part[0].isalpha():  # 텍스트가 문자로 시작하면 새로운 컬럼명(Key)으로 인식
                    if not part in obj:
                        obj[part] = ''
                        key.append(part)
                else:  # 텍스트가 숫자로 시작하면 직전 컬럼명의 값(Value)으로 매핑 및 괄호 제거
                    if key:
                        obj[key[-1]] = part.split(' ')[-1].replace("(", "").replace(")", "")
            data.append(obj)

        # 4. 개별 연도 데이터프레임 가공
        df = pd.DataFrame(data).set_index('date').sort_index()
        # 비율(Ratio) 데이터를 제외하고 괄호"()"가 포함된 메인 수치 컬럼만 필터링 및 이름 변경
        cols = {c: c.split(" ")[0] for c in df.columns if not c.startswith("Ratio") and "(" in c}
        objs.append(df[cols.keys()].rename(columns=cols))

        # 서버 과부하 방지를 위한 대기 시간
        time.sleep(0.5)

    # 5. 전체 연도 데이터 병합 및 최종 데이터 정제
    df = pd.concat(objs, axis=0)
    # 천 단위 콤마(,) 및 마침표(.)를 제거한 후 정수형 데이터로 변환
    for c in df.columns:
        df[c] = df[c].str.replace(",", "").str.replace(".", "").astype(int)
    # 인덱스를 Datetime 타입으로 변환 후 날짜 오름차순 정렬
    df.index = pd.to_datetime(df.index)
    return df.sort_index()

def crude_oil_stocks() -> DataFrame:
    """
    EIA(미국 에너지정보청) 공식 웹사이트에서 원유 재고 데이터를 실시간으로 읽어와 병합합니다.

    Returns:
        DataFrame: 미국 상업용 원유 재고('Commercial')와 전략비축유('SPR') 데이터를
                   날짜('Date') 인덱스 기준으로 병합한 데이터프레임 (단위: 천 배럴)
    """
    commercial = pd.read_excel(
        'https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls',
        sheet_name='Data 1',
        skiprows=2,
    ).set_index('Date')

    spr = pd.read_excel(
        'https://www.eia.gov/dnav/pet/hist_xls/WCSSTUS1w.xls',
        sheet_name='Data 1',
        skiprows=2
    ).set_index('Date')

    data = pd.concat([commercial, spr], axis=1)
    data.columns = ['Commercial', 'SPR']
    return data


if __name__ == "__main__":

    # print(baker_hughes_rig_count(2026, verify=False))
    # print(baker_hughes_rig_count())
    print(crude_oil_stocks())
