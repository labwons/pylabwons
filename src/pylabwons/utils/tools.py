from pandas import Series, Index
from typing import Union
import numpy as np
import pandas as pd


def align_series(indicator: Series, asset: Series):
    """
    서로 다른 주기(Daily, Weekly, Monthly)를 가진 두 시계열 데이터프레임을
    더 빈도가 낮은(샘플이 적은) 시계열 주기에 맞춰 정렬

    Parameters:
        indicator, asset (pd.Series): DatetimeIndex를 가진 데이터프레임
    Returns:
        pd.DataFrame: 정렬 및 결합이 완료된 데이터프레임 (결측치 없음)
    """
    # 1. 고유한 날짜 수(길이)를 비교하여 기준 시계열(Low Freq)과 대상 시계열(High Freq) 판단
    if len(indicator.index.unique()) <= len(asset.index.unique()):
        df_low, df_high = indicator, asset
    else:
        df_low, df_high = asset, indicator

    # 2. 고빈도(샘플이 많은) 데이터를 일별(Daily Calendar) 주기로 확장 후 직전 값으로 채움
    # 이 과정에서 주말/휴장일 등으로 인한 공백이 직전 영업일 데이터로 메워집니다.
    df_high_daily = df_high.resample('D').ffill()

    # 3. 저빈도(샘플이 적은) 데이터의 실제 타임스탬프 위치의 데이터만 고빈도 데이터에서 추출
    df_high_matched = df_high_daily.reindex(df_low.index, method='ffill')

    # 4. 두 데이터 결합 (인덱스가 완전히 일치하므로 데이터 유실 없음)
    df_aligned = pd.concat([df_low, df_high_matched], axis=1)

    # 5. 혹시 모를 초기 결측치(High Freq 데이터의 시작일이 Low Freq보다 늦을 경우) 제거
    return df_aligned.dropna()

def int2krw(krw: Union[int, float], limit:str='억') -> Union[str, float]:
    """
    KRW (원화) 입력 시 화폐 표기 법으로 변환(자동 계산)
    @krw 단위는 원 일 것
    """
    if pd.isna(krw) or np.isnan(krw):
        return np.nan
    if krw >= 1e+12:
        krw /= 1e+8
        currency = f'{int(krw // 10000)}조'
        if int(krw % 10000):
            currency += f' {int(krw % 10000)}억'
        return currency
    if krw >= 1e+8:
        krw /= 1e+4
        currency = f'{int(krw // 10000)}억'
        if limit == '억':
            return currency
        if int(krw % 10000):
            currency += f' {int(krw % 10000)}만'
        return currency
    return f'{int(krw // 10000)}만'

def detect_frequency(series: Union[Index, Series]):
    """
    비규칙적인 시계열 인덱스의 실제 주기를 판별합니다.

    Parameters:
    series_index (pd.DatetimeIndex): 시계열 데이터의 datetime 인덱스

    Returns:
    str: 'Daily' (일간), 'Weekly' (주간), 'Monthly' (월간), 'Unknown' (판별 불가)
    """
    if len(series) < 3:
        raise ValueError('Too few samples to detect')

    # 1. 인덱스 정렬 및 날짜 차이(일 단위) 계산
    sorted_index = series.sort_values()
    day_gaps = sorted_index.to_series().diff().dt.days.dropna()

    # 2. 통계치 산출 (최빈값, 중앙값, 최대값)
    mode_gap = day_gaps.mode().iloc[0] if not day_gaps.empty else 0
    median_gap = day_gaps.median()
    max_gap = day_gaps.max()

    # 3. 조건별 주기 판별

    # [일간 데이터 판별]
    # 주된 격차가 1일이거나, 주말/연휴를 고려해 중앙 격차가 1~2일 사이인 경우
    # 영업일 기준 일간 데이터는 주말 때문에 max_gap이 3~4일이 될 수 있음
    if mode_gap == 1 or (1 <= median_gap <= 1.5):
        if max_gap > 10:
            return "d"  # 일간 데이터이나 중간에 큰 공백이 있음
        return "d"

    # [주간 데이터 판별]
    # 중앙값이나 최빈값이 7일 근처(5~8일)인 경우
    elif 5 <= median_gap <= 8 or 5 <= mode_gap <= 8:
        # 주간 데이터에서 몇 달 치 데이터가 통째로 빠진 경우를 체크
        if max_gap > 35:
            return "w"
        return "w"

    # [격주간 데이터 (Bi-weekly)] - 신규 추가
    # 격차가 대략 12~16일 사이인 경우 (2주 기준)
    elif 12 <= median_gap <= 16 or 12 <= mode_gap <= 16:
        # 두 달 치(70일) 이상의 데이터 공백이 있는지 체크
        if max_gap > 70:
            return "bw"
        return "bw"

    # [월간 데이터 판별]
    # 중앙 격차가 25일에서 32일 사이인 경우
    elif 25 <= median_gap <= 32:
        if max_gap > 95:
            return "m"
        return "m"

    else:
        raise ValueError('Unable to detect frequency')