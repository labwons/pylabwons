from pylabwons.typesys import classproperty, Path
from pandas import DataFrame
import os


PROJECT_NAME = "pylabwons"
PROJECT_PATH = f"{os.path.dirname(__file__)[:os.path.dirname(__file__).rindex(PROJECT_NAME)]}"


class ARCHIVE_LOCAL:

    def __init__(self, root:str = ''):
        self.root = root = Path(root) if root else Path(os.path.join(PROJECT_PATH, 'labwons-archive'))
        self.logs = root['logs']
        self.tickers = root['tickers']
        self.finance = root['finance']
        self.ohlcv = root['ohlcv']
        self.index = root['index']

    @property
    def files(self) -> DataFrame:
        data = []
        for root, _, files in os.walk(self.root):
            for file in files:
                dirs = root.split(os.sep)
                name, extension = file.split('.')
                path = os.path.join(root, file)
                date = dirs[-1] if 'tickers' in dirs else ''
                data.append({
                    'name': name,
                    'extension': extension,
                    'path': path,
                    'date': date
                })
        return DataFrame(data)


class ARCHIVE:
    root = r'https://github.com/labwons/labwons-archive/raw/refs/heads/main'
    tickers = f'{root}/tickers/tickers.parquet'


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    print(PROJECT_NAME)
    print(PROJECT_PATH)
    print(ARCHIVE_LOCAL.root)
    print(ARCHIVE_LOCAL.tickers)
