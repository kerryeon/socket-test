from socket_test.log import Logger
from socket_test.model import AbstractField
from socket_test.serial import Serial


class Terminate:

    @classmethod
    def _get_name(cls):
        return cls.__name__


class Node:
    next = None
    __cases__ = None
    __serial__ = None

    def process(self):
        pass

    def __init__(self, socket):
        self._socket = socket
        self._get_next()

    def _process(self):
        self.process()
        self._update()

    def _send(self):
        send = self.__serial__.encode()
        self._socket.send(send)
        recv = self._socket.recv(4096)
        return recv

    def _recv(self, data):
        kwargs = self.__serial__.recv(data)
        self._apply(kwargs)
        return self

    def _apply(self, kwargs, force: bool = True):
        for name, value in self.__serial__.match(kwargs, force).items():
            setattr(self, name, value.to_value())
        return self

    def _update(self):
        self.__serial__.match(self.__dict__)

    def _next(self):
        _next = self._get_next_instance()
        if _next is not None:
            Logger.info('[%s\t] %s -> %s' % (self._get_type_name(), self._get_name(), _next._get_name()))
            self._process()
            return _next(self._socket)._recv(self._send())._next()
        else:
            self.process()
            self._socket.close()
            return None

    def _get_next_instance(self):
        return self._get_next()

    @classmethod
    def _get_next(cls):
        if not cls._use_next():
            return None
        assert cls.next is not None, '%s must point to Next.' % cls._get_name()
        if issubclass(cls.next, Terminate):
            return None
        assert issubclass(cls.next, Node), '%s must point to the correct Next.' % cls._get_name()
        return cls.next

    @classmethod
    def _collect(cls):
        if cls.__serial__ is not None:
            return cls.__serial__

        cls.__serial__ = Serial(cls._get_name(), cls._use_op())
        if cls._collect_serial_pre():
            cls._collect_serial()

        _next = cls._get_next()
        if _next is not None:
            _next._collect()

    @classmethod
    def _collect_serial_pre(cls):
        return True

    @classmethod
    def _collect_serial(cls):
        for name, target in cls.__dict__.items():
            if isinstance(target, AbstractField):
                cls.__serial__.add_argument(name, target)

    @classmethod
    def _collect_nodes(cls):
        for name, target in cls.__dict__.items():
            try:
                if issubclass(target, Node):
                    yield name, target
            except TypeError:
                pass

    @classmethod
    def _collect_dict_self(cls, root: list):
        root.append(cls._to_dict())

    @classmethod
    def _collect_dict_next(cls, root: list):
        _next = cls._get_next()
        if _next is not None:
            _next._collect_dict(root)

    @classmethod
    def _collect_dict_cases(cls, root: list):
        if not cls._use_cases():
            return
        for target in cls.__cases__.get_next_iter():
            target._collect_dict(root)

    @classmethod
    def _collect_dict(cls, root: list):
        cls._collect_dict_self(root)
        cls._collect_dict_cases(root)
        cls._collect_dict_next(root)

    @classmethod
    def _use_op(cls):
        return False

    @classmethod
    def _use_cases(cls):
        return False

    @classmethod
    def _use_fields(cls):
        return True

    @classmethod
    def _use_next(cls):
        return True

    @classmethod
    def _use_settings(cls):
        return False

    @classmethod
    def _to_dict(cls):
        default = {
            'name': cls._get_name(),
            'type': cls._get_type_name(),
        }
        if cls._use_op():
            default['op'] = cls.__serial__.get_op()
        if cls._use_cases():
            default['cases'] = cls.__cases__.to_dict()
        if cls._use_fields():
            default['fields'] = cls.__serial__.to_dict()
        if cls._use_next():
            default['next'] = cls.next._get_name()
        if cls._use_settings():
            default['settings'] = {}
        return default

    @staticmethod
    def _get_type_name():
        raise NotImplementedError

    @classmethod
    def _get_name(cls):
        return cls.__name__
