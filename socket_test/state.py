from socket_test.log import Logger
from socket_test.response import Response


class NextState:
    def __init__(self, name):
        self._name = name
        self._dict = {}

    def add_next(self, name, target):
        self._dict[name] = target

    def get_next_iter(self):
        return iter(self._dict.values())

    def to_dict(self):
        return [
            target._get_name()
            for target in self._dict.values()
        ]


class Update(Response):
    def process(self):
        raise NotImplementedError

    def _next(self):
        return self.process()

    @classmethod
    def _use_next(cls):
        return False

    @staticmethod
    def _get_type_name():
        return Update.__name__


class State(Response):
    def process(self):
        yield None, {}

    def _process(self):
        for op, kwargs in self.process():
            assert isinstance(kwargs, dict)
            self._update()
            yield op, kwargs

    def _next(self):
        for op, kwargs in self._process():
            if op is None:
                self._socket.close()
                return
            assert not issubclass(op, State), 'You cannot specify a state immediately in %s. ' \
                                              'Instead, use the Node to mediate.' % self._get_name()
            Logger.info('[%s\t] %s -> %s' % (self._get_type_name(), self._get_name(), op._get_name()))
            kwargs = op(self._socket)._apply(kwargs)._next()
            assert isinstance(kwargs, dict)
            self._apply(kwargs, force=False)

    @classmethod
    def _collect(cls):
        super()._collect()
        cls.__cases__ = next_state = NextState(cls._get_name())
        for name, target in cls._collect_nodes():
            next_state.add_next(name, target)
            target._collect()

    @classmethod
    def _use_cases(cls):
        return True

    @classmethod
    def _use_next(cls):
        return False

    @staticmethod
    def _get_type_name():
        return State.__name__
