class _MpWritable:

    def __init__(self):
        self._result = ''

    def to_string(self, indent: int = 0):
        self._result = ''
        self._to_string(indent)
        return self._result[:-1]

    def _add_line(self, message: str, indent: int = 0):
        self._result += '\t' * indent + message + '\n'

    def _to_string(self, indent: int):
        raise NotImplementedError
