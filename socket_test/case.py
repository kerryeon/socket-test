from socket_test.model import UIntFlexible
from socket_test.response import Response


class EnumNext:
    def __init__(self, name):
        self._name = name
        self._list_name = []
        self._list_next = []

    def add(self, name, target):
        assert len(self) < 255, 'You have set too many Cases in the Enum.'
        self._list_name.append(name)
        self._list_next.append(target)

    def get(self, idx):
        assert 0 <= idx < len(self)
        return self._list_next[idx]

    def to_dict(self):
        return {
            idx: target._get_name()
            for idx, target in enumerate(self._list_next)
        }

    def get_next_iter(self):
        return iter(self._list_next)

    def __len__(self):
        return len(self._list_name)


class Case(Response):
    __case__ = None
    __data__ = None

    def _send(self):
        return self.__data__

    def _recv(self, data):
        self.__data__ = data[1:]
        return super()._recv(data)

    def _get_next_instance(self):
        return self.__cases__.get(self.__case__)

    @classmethod
    def _collect(cls):
        super()._collect()
        cls.__cases__ = enum = EnumNext(cls._get_name())
        for name, target in cls._collect_nodes():
            enum.add(name, target)
            target._collect()
        cls.__case__.set_size(len(enum))

    @classmethod
    def _collect_serial_pre(cls):
        cls.__case__ = case = UIntFlexible()
        cls.__serial__.add_argument('__case__', case)
        return False

    @classmethod
    def _use_cases(cls):
        return True

    @classmethod
    def _use_fields(cls):
        return False

    @classmethod
    def _use_next(cls):
        return False

    @staticmethod
    def _get_type_name():
        return Case.__name__
