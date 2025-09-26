

class URL:

    REPO = r'https://github.com/labwons/labwons-archive/raw/refs/heads/main'
    TICKERS = f'{REPO}/tickers/tickers.parquet'

    def __class_getitem__(cls, item):
        return f'{cls.REPO}/ohlcv/{item}.parquet'