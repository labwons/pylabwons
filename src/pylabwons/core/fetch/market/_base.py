from pylabwons.utils.logger import Logger
from pandas import DataFrame
from typing import Union
import pandas as pd
import io, requests, urllib3

# InsecureRequestWarning 경고 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class _BaseDataFrame(DataFrame):

    _metadata = ['logger']

    @property
    def _constructor(self):
        return _BaseDataFrame

    def __init__(self, *args, **kwargs):
        self.logger:Union[Logger, print] = kwargs.get('logger', print)

        data = args[0]
        if isinstance(data, DataFrame):
            super().__init__(data)
            return

        if isinstance(data, str):
            src = ''
            if data.startswith('http'):
                resp = requests.get(data, verify=False)
                if not resp.status_code == 200:
                    self.logger(f'Error parsing: {resp.status_code}')
                    super().__init__()
                    return
                src = io.BytesIO(resp.content)

            if data.endswith('.parquet'):
                try:
                    super().__init__(pd.read_parquet(src, engine='pyarrow'))
                except (FileExistsError, FileNotFoundError, IndexError, KeyError, Exception) as e:
                    self.logger(f'Error parsing: {e}')
                    super().__init__()
                return

        super().__init__()
        return