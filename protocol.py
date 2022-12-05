import pickle
import socket

class BingoProtocol:
    def send(sock: socket, msg):
        msg_size = len(msg).to_bytes(2, "big")
        msg_to_send = msg_size + msg
        while len(msg_to_send) > 0:
            sent = sock.send(msg_to_send)
            msg_to_send = msg_to_send[sent:]

    def rcv(sock : socket):
        msg_size= int.from_bytes(sock.recv(2), "big")
        if msg_size != 0:
            msg=b""
            while len(msg) < msg_size:
                msg += sock.recv(msg_size - len(msg))
            return pickle.loads(msg)

    def join(sock: socket):
        msg = pickle.dumps({"type": "join", "host": sock.getsockname()})
        BingoProtocol.send(sock, msg)

    def ack(sock: socket, command):
        msg = pickle.dumps({"type": "ack", "command": command})
        BingoProtocol.send(sock, msg)