from socket_test.node import Node


class Request(Node):

    @classmethod
    def _use_op(cls):
        return True

    @staticmethod
    def _get_type_name():
        return Request.__name__
