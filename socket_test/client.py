import socket
import threading

from socket_test.response import Response
from socket_test.log import Logger
from socket_test.op import OpCodeMonitor


class Client(Response):
    Settings = None

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.__class__.Settings.IP, self.__class__.Settings.PORT))
        super().__init__(sock)

    @classmethod
    def build(cls):
        Logger.init()
        OpCodeMonitor.init(cls.Settings.MODEL_PATH if hasattr(cls.Settings, 'MODEL_PATH') else None)

        Logger.info('Collecting system...')
        cls._collect()
        Logger.info('Collecting system completed.')

        Logger.info('Backing up and Saving system...')
        json_raw = []
        cls._collect_dict(json_raw)
        OpCodeMonitor.update(json_raw)
        Logger.info('Saving system completed.')

    @classmethod
    def begin_test(cls, **kwargs):
        threading.Thread(target=cls()._next, kwargs=kwargs).start()

    def _next(self, **kwargs):
        OpCodeMonitor.get()
        _next = self._get_next()
        if _next is not None:
            return _next(self._socket)._apply(kwargs)._next()
        else:
            raise Exception('You cannot point to Terminate at the beginning.')

    @classmethod
    def _use_fields(cls):
        return False

    @classmethod
    def _use_settings(cls):
        return True

    @staticmethod
    def _get_type_name():
        return Client.__name__
