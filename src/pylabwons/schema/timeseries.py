from dateutil.relativedelta import relativedelta
from pandas import DataFrame
import pandas as pd


class TimeSeriesSlicer:
    """
    날짜 시계열 인덱스를 가진 판다스 데이터프레임을 자동으로 슬라이싱하는 클래스입니다.
    마지막 일자 기준 [전체, 1/2, 1/4, ...] 형태로 데이터프레임을 슬라이싱합니다.
    최대 기간은 원본 데이터프레임의 전체 기간입니다.
    """

    def __call__(self) -> DataFrame:
        return pd.concat(self.objs, axis=1)

    def __getitem__(self, key) -> DataFrame:
        return self.objs[key]

    def __init__(self, data: DataFrame, base_months=6):
        """
        :param data: 날짜 시계열 인덱스를 가진 판다스 데이터프레임
        :param base_months: 가장 짧은 슬라이싱 기간 (기본값: 6개월)
        """
        self.data = data.copy()
        self.dates = []
        self.objs = {}

        df, first_date, end_date = data.sort_index(), data.index[0], data.index[-1]
        i = 0
        while True:
            months_to_subtract = base_months * (2 ** i)
            start_date = end_date - relativedelta(months=months_to_subtract)
            self.dates.append(start_date)

            if start_date <= first_date:
                self.objs["ALL"] = df
                break

            sliced_df = df.loc[start_date:end_date]

            if months_to_subtract < 12:
                key_name = f"{months_to_subtract}M"
            else:
                key_name = f"{months_to_subtract // 12}Y"
                if months_to_subtract % 12 != 0:
                    key_name += f" {months_to_subtract % 12}M"

            self.objs[key_name] = sliced_df
            i += 1

        return

    def __iter__(self):
        for key in self.objs:
            yield key, self.objs[key]
