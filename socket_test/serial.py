from socket_test.op import OpCodeMonitor


class Serial:
    def __init__(self, name: str, use_op: bool):
        self._name = name
        self._dict = {}
        self._op = OpCodeMonitor.get_op(name) if use_op else None

    def add_argument(self, name, target):
        self._dict[name] = target

    def match(self, kwargs, force: bool = True):
        if not force:
            return self._match_no_force(kwargs)
        for name, target in self._dict.items():
            assert name in kwargs, 'Argument "%s" is missing.' % name
            target.set(kwargs[name])
        return self._dict

    def _match_no_force(self, kwargs):
        for name, target in self._dict.items():
            if name in kwargs:
                target.set(kwargs[name])
        return self._dict

    def recv(self, data):
        idx = 0
        kwargs = {}
        for name, target in self._dict.items():
            kwargs[name] = target.decode(data[idx:])
            idx += target.get_size()
        return kwargs

    def encode(self):
        data = self._op.encode() if self._op is not None else b''
        for target in self._dict.values():
            data += target.encode()
        return data

    def get_op(self):
        return self._op.get_value()

    def to_dict(self):
        return [{
            'name': name,
            'type': target.get_type(),
        } for name, target in self._dict.items()]
