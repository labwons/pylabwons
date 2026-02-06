from io import StringIO
import logging, time


class Logger(logging.Logger):

    @classmethod
    def kst(cls, *args):
        return time.localtime(time.mktime(time.gmtime()) + 9 * 3600)

    def __init__(self, console:bool=True):
        formatter = logging.Formatter(
            fmt=f"%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = self.kst
        super().__init__(name='pylabwons', level=logging.DEBUG)
        self.propagate = False

        self._buffer = StringIO()
        stream_handler = logging.StreamHandler(stream=self._buffer)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)

        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.addHandler(console_handler)

        self._held = ''
        self._time = None
        return

    def __call__(self, io:str, end:str=''):
        if end:
            self.hold(f'{io}{end}')
        else:
            self.eol(io)
        return

    def __str__(self) -> str:
        return self._buffer.getvalue()

    def eol(self, msg:str='', *args, **kwargs):
        if self._held:
            msg = self._held + msg
        super().info(msg, *args, **kwargs)
        self._held = ''
        return

    def hold(self, msg:str):
        self._held += msg

    def tic(self, context:str=''):
        if context:
            self.info(context)
        self._time = time.perf_counter()
        return

    def toc(self, context:str=''):
        try:
            context = f'{context} {time.perf_counter() - self._time:.2f}s'
            self.info(context)
        except (AttributeError, TypeError, Exception):
            raise RuntimeError('Logger is not started. Please call .run() method first.')
        return

    def to_file(self, file:str=''):
        with open(file, 'r', encoding="utf-8") as f:
            f.write(str(self))
        return