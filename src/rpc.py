from enum import Enum
import socket
import struct


class RPCHead(Enum):
    Ping = 1
    HeartBeat = 2
    Data = 3
    Close = 4


def rpc_head_to_int(rpc_head: RPCHead):
    if rpc_head is RPCHead.Ping:
        return 1
    if rpc_head is RPCHead.HeartBeat:
        return 2
    if rpc_head is RPCHead.Data:
        return 3
    if rpc_head is RPCHead.Close:
        return 4


class MessageHandler(object):
    message_queue = []

    def __init__(self, socket0):
        self.socket: socket.socket = socket0

    def pack(self, head: RPCHead, body=None):
        resp = bytearray()
        resp += struct.pack(">I", rpc_head_to_int(head))
        if head is RPCHead.Data:
            idx, x, y = body
            resp += struct.pack(">I", idx)
            resp += struct.pack(">d", x)
            resp += struct.pack(">d", y)
        return resp

    def recv(self):
        head = self.socket.recv(4)
        head_code = struct.unpack(">I", head)[0]
        if head_code > 4 or head_code == 0:
            return  # 丢弃
        if head_code == 3:  # 匹配Data
            idx = struct.unpack(">I", self.socket.recv(4))[0]
            x = struct.unpack(">d", self.socket.recv(8))[0]
            y = struct.unpack(">d", self.socket.recv(8))[0]
            self.message_queue.append((
                3, (idx, x, y)
            ))


class RPCServer(object):
    client_socket: socket.socket

    def __init__(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, port=3089):
        self.socket.bind(("127.0.0.1", port))
        self.socket.listen(128)

    def accept_loop(self):
        while True:
            self.client_socket, client_address = self.socket.accept()
            message_handler = MessageHandler(self.client_socket)
            while True:
                message_handler.recv()


# to do : 把RPC实装