from pylabwons.util.path import PROJECT_DATA
from datetime import datetime
import logging, time, os


class Logger(object):

    _onoff = False
    _timer = None

    @classmethod
    def kst(cls, *args):
        return time.localtime(time.mktime(time.gmtime(*args)) + 9 * 3600)

    def __init__(self):
        self.file = file = os.path.join(PROJECT_DATA.logs, f'{datetime.today().strftime("%Y-%m-%d")}.log')

        self.logger = logging.getLogger("pylabwons")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        formatter = logging.Formatter(
            fmt=f"%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = self.kst

        file_handler = logging.FileHandler(file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        return

    def __getattr__(self, item):
        if hasattr(self.logger, item):
            if not self._onoff:
                return str
            return getattr(self.logger, item)
        try:
            return getattr(self, item)
        except AttributeError:
            raise AttributeError(f"'Logging' object has no attribute '{item}'")

    def read(self, date:str=''):
        if not date:
            file = self.file
        else:
            file = os.path.join(PROJECT_DATA.logs, f'{date}.log')
        with open(file, 'r', encoding="utf-8") as f:
            return f.read()

    def on(self):
        self._onoff = True
        self._timer = time.perf_counter()

    def off(self):
        self._onoff = False

    def runtime(self) -> str:
        try:
            return f'{time.perf_counter() - self._timer:.2f}s'
        except (AttributeError, Exception):
            raise RuntimeError('Logger is not started. Please call .on() method first.')
