from pylabwons.typesys import DataDictionary
from pandas import DataFrame
import os


PROJECT_NAME = "pylabwons"
PROJECT_PATH = f"{os.path.dirname(__file__)[:os.path.dirname(__file__).rindex(PROJECT_NAME)]}{PROJECT_NAME}"

class _data(DataDictionary):

    def __init__(self, date:str=''):
        super().__init__(
            root=os.path.join(PROJECT_PATH, 'data'),
            logs=os.path.join(PROJECT_PATH, 'data', 'logs'),
            tickers=os.path.join(PROJECT_PATH, 'data', 'tickers'),
            timeseries=os.path.join(PROJECT_PATH, 'data', 'timeseries'),
            finance=os.path.join(PROJECT_PATH, 'data', 'finance'),
            date=date
        )
        os.makedirs(self.logs, exist_ok=True)
        os.makedirs(self.timeseries, exist_ok=True)
        os.makedirs(self.tickers, exist_ok=True)
        os.makedirs(self.finance, exist_ok=True)
        return

    # def __iter__(self):
    #     for ticker in os.listdir(self.tickers):
    #         yield ticker.split('.')[0]

    @classmethod
    def create(cls, file:str):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        return file

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


# Alias
ARCHIVE = DATA = PROJECT_DATA = _data()


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    print(PROJECT_NAME)
    print(PROJECT_PATH)
    print(PROJECT_DATA)
    print(PROJECT_DATA.files)