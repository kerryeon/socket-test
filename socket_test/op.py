import json
import os

from mp import encode

from socket_test import __version__
from socket_test.log import Logger
from socket_test.model import UInt8Field


class OpCodeMonitor:
    __unique__ = None

    MODEL_PATH = './settings.json'

    def __init__(self):
        self._model = UInt8Field()
        self._ops = {}

    @classmethod
    def get(cls):
        assert cls.__unique__ is not None, 'Please build ahead.'
        return cls.__unique__

    @classmethod
    def init(cls, model_path: str):
        assert cls.__unique__ is None
        cls.MODEL_PATH = model_path or cls.MODEL_PATH
        cls.__unique__ = cls()
        cls.get_op('__close__')

    @classmethod
    def update(cls, json_raw: list):
        json_last = cls.load_last_setting()

        for node in json_raw:
            for node_last in json_last:
                if node['name'] != node_last['name']:
                    continue
                if 'op' in node:
                    if node['op'] != node_last['op']:
                        Logger.print('%s.op: %d -> %d' % (node['name'], node_last['op'], node['op']))
                        print(node_last)

        with open(cls.MODEL_PATH[:-5] + '.mp', 'w') as fp:
            fp.write(encode(json_raw, __version__.__name__))

        with open(cls.MODEL_PATH, 'w') as fp:
            json.dump(json_raw, fp, indent='\t')

    @classmethod
    def get_op(cls, name: str):
        self = cls.get()
        value = len(self._ops)
        op = OpCode(name, value)
        self._ops[name] = op
        return op

    @classmethod
    def encode(cls, value: int):
        self = cls.get()
        model = self._model
        model.set(value)
        return model.encode()

    @classmethod
    def load_last_setting(cls):
        if os.path.exists(cls.MODEL_PATH):
            Logger.info('Found setting file from "%s".' % cls.MODEL_PATH)
            with open(cls.MODEL_PATH, 'r') as fp:
                return json.load(fp)
        Logger.info('Skipping loading setting file from "%s".' % cls.MODEL_PATH)
        return None


class OpCode:
    def __init__(self, name: str, value: int):
        self._name = name
        self._value = value

    def encode(self):
        return OpCodeMonitor.encode(self.get_value())

    def get_value(self):
        return self._value
