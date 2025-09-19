import logging, time


class Logger(logging.Logger):

    _timer = None

    @classmethod
    def kst(cls, *args):
        return time.localtime(time.mktime(time.gmtime()) + 9 * 3600)

    def __init__(self, file:str):

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

        super().__init__(name='pylabwons', level=logging.DEBUG)

        self.propagate = False
        self.file = file


        if not self.handlers:
            self.addHandler(file_handler)
            self.addHandler(console_handler)
        return

    def read(self, file:str=''):
        if not file:
            file = self.file
        with open(file, 'r', encoding="utf-8") as f:
            return f.read()

    def run(self, context:str=''):
        if context:
            self.info(context)
        self._timer = time.perf_counter()
        return

    def end(self, context:str=''):
        try:
            context = f'{context} {time.perf_counter() - self._timer:.2f}s'
            self.info(context)
        except (AttributeError, TypeError, Exception):
            raise RuntimeError('Logger is not started. Please call .run() method first.')
        return
