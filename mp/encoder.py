from mp.object import MpObject


class MpWriter:

    def __init__(self, *using):
        self._c = dict()
        if len(using) > 0:
            self._c['Using'] = MpObject.from_python(using, 'Using')

    def put(self, data: list):
        assert isinstance(data, list)
        for c in data:
            obj = MpObject.from_python(c)
            self._c[obj.name] = obj

    def __str__(self):
        _result = ''
        for c in self._c.values():
            _result += str(c) + '\n' * 2
        return _result[:-1]


def encode(data: list, *using):
    writer = MpWriter(*using)
    writer.put(data)
    return str(writer)
