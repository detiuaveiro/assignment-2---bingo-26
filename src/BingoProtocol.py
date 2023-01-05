import pickle
import socket

class BingoProtocol:

    def __init__(self):
        pass


    def msg_handler(func):
        """
        Decorator to handle sending messages
        """
        def wrapper(*args, **kwargs):
            msg = {
                "type": func.__name__,
                "data": func(*args, **kwargs)
            }
            if args[1] is not None:
                args[0].send(args[1], pickle.dumps(msg))
            return msg
        return wrapper


    @msg_handler
    def join(self, sock: socket.socket, client: str): 
        return {
            "client": client
        }


    @msg_handler
    def join_response(self, sock: socket.socket, accepted: bool, sequence_number: int): 
        return {
            "accepted": accepted, 
            "SN": sequence_number
        }


    def send(self, sock: socket.socket, msg: bytes):
        msg_size = len(msg).to_bytes(4, "big")
        msg_to_send = msg_size + msg
        while len(msg_to_send) > 0:
            sent = sock.send(msg_to_send)
            msg_to_send = msg_to_send[sent:]
            

    def rcv(self, sock : socket.socket):
        msg_size = int.from_bytes(sock.recv(4), "big")
        if msg_size != 0:
            msg=b""
            while len(msg) < msg_size:
                msg += sock.recv(msg_size - len(msg))
            return pickle.loads(msg)