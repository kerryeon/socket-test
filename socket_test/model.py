class AbstractField:
    def __init__(self, size):
        self._size = size
        self._value = None
        self._test_size()

    def _test_size(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError

    def to_value(self):
        assert self._value is not None
        return self._value

    def get_size(self):
        return self._size

    def encode(self):
        raise NotImplementedError

    def decode(self, data: bytes):
        raise NotImplementedError

    @classmethod
    def get_type(cls):
        return cls.__name__


class StaticField(AbstractField):
    def _test_size(self):
        assert isinstance(self._size, int)
        assert self._size > 0


class AbstractFlexible(StaticField):
    __rep__ = {}

    def __init__(self, size_default=1):
        super().__init__(size_default)
        self._rep = None
        self.set_size(size_default)

    def _test_size(self):
        super()._test_size()
        for size in self.__rep__:
            if self._size == size:
                return
        raise Exception('Received a size that is not in __rep__.')

    def set_size(self, size_bytes):
        self._size = 0
        while size_bytes >= 1:
            self._size += 1
            size_bytes >>= 8
        self._test_size()
        rep_cls = self.__rep__[self._size]
        if type(self._rep) is not rep_cls:
            self._rep = rep_cls()

    def set(self, value):
        self._rep.set(value)

    def to_value(self):
        return self._rep.to_value()

    def encode(self):
        return self._rep.encode()

    def decode(self, data: bytes):
        return self._rep.decode(data)


class DynamicField(AbstractField):
    def __init__(self, size=(1, 1)):
        super().__init__(size)

    def _test_size(self):
        assert len(self._size) == 2
        assert isinstance(self._size[0], int)
        assert isinstance(self._size[1], int)
        assert self._size[0] > 0
        assert self._size[0] <= self._size[1]


class UInt8Field(StaticField):
    def __init__(self):
        super().__init__(1)

    def set(self, value):
        assert isinstance(value, int)
        assert value >= 0
        assert value < 256
        self._value = value

    def encode(self):
        return self.to_value().to_bytes(self._size, 'big', signed=False)

    def decode(self, data: bytes):
        value = data[0]
        self.set(value)
        return value


class UIntFlexible(AbstractFlexible):
    __rep__ = {
        1: UInt8Field
    }
