from pylabwons.typesys import DataDictionary
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

    def __iter__(self):
        for ticker in os.listdir(self.tickers):
            yield ticker.split('.')[0]
# Alias
PROJECT_DATA = DATA= _data()

if __name__ == "__main__":
    print(PROJECT_NAME)
    print(PROJECT_PATH)
    print(PROJECT_DATA)