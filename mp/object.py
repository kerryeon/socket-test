from mp.base import _MpWritable


class MpObject(_MpWritable):

    __default__ = ['name', 'type', 'value', 'length', ]

    def __init__(self, data, name: str = None):
        super(_MpWritable).__init__()
        assert isinstance(data, dict)
        assert name or 'name' in data
        self._name = name or data['name']
        self._type = self._get('type', data)
        self._value = self._get('value', data)
        self._length = self._get('length', data)
        self._param = {
            name: self.from_python(value, name)
            for name, value in data.items()
            if name not in self.__default__
        }

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type or self._value

    @property
    def length(self):
        length = self._length
        if length is None:
            return None
        if length == 0:
            return ''
        return self._length

    def add(self, obj):
        self._param[obj.name] = obj

    def _to_string(self, indent: int):
        self._result = ''
        length = self.length
        name = self.name if length is None else '%s[%s]' % (self.name, length)
        t = self.type
        self._add_line('%s: %s' % (name, t) if t
                       else '%s:' % name if len(self._param) > 0
                       else name
                       , indent)
        indent += 1
        for c in self._param.values():
            self._add_line(c.to_string(indent))
        return self._result

    @classmethod
    def _get(cls, name: str, data: dict):
        return data[name] if name in data else None

    @classmethod
    def _get_length(cls, name: str, data: dict):
        length = cls._get(name, data)
        assert isinstance(length, int)
        assert length >= 0

    @classmethod
    def from_python(cls, data, name: str = None):
        return MpObject(data, name) if isinstance(data, dict) \
            else MpArray(data, name) if isinstance(data, list) or isinstance(data, tuple) \
            else cls.from_raw(data, name) if name is not None \
            else cls.empty(data)

    @classmethod
    def from_raw(cls, value, name: str):
        return MpObject({'name': name, 'value': value})

    @classmethod
    def empty(cls, name: str):
        return MpObject({'name': name})

    def __str__(self):
        return self.to_string(indent=0)


class MpArray(MpObject):

    def __init__(self, data: list, name: str = None):
        super().__init__({'length': 0}, name)
        for raw in data:
            c = self.from_python(raw)
            self._param[c.name] = c
