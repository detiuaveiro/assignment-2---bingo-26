import pickle
import socket

class BingoProtocol:

    def __init__(self):
        self.msg = None


    def join(self, sock: socket.socket, client: str):
        host, port = sock.getsockname()
        self.msg = { 
            "type": "join", 
            "data" : {
                "client": client,
                "host": host, 
                "port": port
            }
        }
        self.send(sock, pickle.dumps(self.msg))

    
    def join_response(self, sock: socket.socket, accepted: bool):
        self.msg = {
            "type": "join_response", 
            "data": {
                "accepted": accepted
            }
        }
        self.send(sock, pickle.dumps(self.msg))


    def send(self, sock: socket.socket, msg: bytes):
        msg_size = len(msg).to_bytes(2, "big")
        msg_to_send = msg_size + msg
        while len(msg_to_send) > 0:
            sent = sock.send(msg_to_send)
            msg_to_send = msg_to_send[sent:]
            

    def rcv(self, sock : socket.socket):
        msg_size = int.from_bytes(sock.recv(2), "big")
        if msg_size != 0:
            msg=b""
            while len(msg) < msg_size:
                msg += sock.recv(msg_size - len(msg))
            return pickle.loads(msg)