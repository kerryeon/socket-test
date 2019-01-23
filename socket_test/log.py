from datetime import datetime
import os
import time


class LogColor:
    if os.name == 'nt':
        Default = ''
        Red = ''
        Yellow = ''
        Green = ''
        Blue = ''
    else:
        Default = '\e[0m'
        Red = '\e[31m'
        Yellow = '\e[33m'
        Green = '\e[32m'
        Blue = '\e[34m'


class LogTick:

    def __init__(self):
        self._time_begin = time.time_ns()

    def __call__(self):
        elapsed_time = time.time_ns() - self._time_begin
        millisecond = elapsed_time // 1e+3
        second = millisecond // 1e+6
        minute = second // 60
        hour = minute // 60
        return '%02d:%02d:%02d.%06d' % (hour % 60, minute % 60, second % 60, millisecond % 1e+6)


class Logger:
    __symbol__ = None
    # __symbol__ = 'SocketTest'

    __default_directory__ = './logs'
    __default_filename__ = 'logs-%y%m%d-%H%M%S.txt'

    _file = None
    _tick = None
    _verbose = True

    @classmethod
    def init(cls, file: str = None, verbose: bool = True):
        file = cls._create_filename(file)
        if file is not None:
            cls._file = open(file, 'w')
        cls._verbose = verbose
        cls._tick = LogTick()
        cls.info('Init...')

    @classmethod
    def info(cls, message: str):
        cls.format('info', message)

    @classmethod
    def format(cls, status: str, message: str, color: str = LogColor.Default):
        message = '[%s][%s] %s %s' % (cls.__symbol__, status, cls._tick(), message) \
            if cls.__symbol__ is not None \
            else '[%s] %s %s' % (status, cls._tick(), message)
        cls.print(message, color)

    @classmethod
    def print(cls, message: str, color: str = LogColor.Default):
        message = color + message
        if cls._file is not None:
            print(message, file=cls._file)
        if cls._verbose:
            print(message)

    @classmethod
    def _create_filename(cls, file: str):
        if cls.__default_directory__ is not None and file is None:
            file = cls.__default_directory__
            if not os.path.exists(file):
                os.mkdir(file)
            return os.path.join(file, datetime.strftime(datetime.now(), cls.__default_filename__))
        return file
