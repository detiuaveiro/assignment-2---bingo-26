import pickle
import socket


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


class BingoProtocol:

    def __init__(self):
        pass

    @msg_handler
    def join(self, sock: socket.socket, cc, client: str, nickname: str, public_key: bytes): 
        return {
            "client": client,
            "nickname": nickname,
            "public_key": public_key
        }


    @msg_handler
    def join_response(self, sock: socket.socket, accepted: bool, sequence_number: int): 
        return {
            "accepted": accepted, 
            "seq": sequence_number
        }

    
    @msg_handler
    def start(self, sock: socket.socket):
        return {}

    
    @msg_handler
    def start_response(self, sock: socket.socket, num_players: int):
        return {
            "num_players": num_players
        }


    @msg_handler
    def card(self, sock: socket.socket, card: list, seq: int):
        return {
            "card": card,
            "seq": seq
        }


    @msg_handler
    def deck(self, sock: socket.socket, deck: list, seq: int):
        return {
            "deck": deck,
            "seq": seq
        }


    @msg_handler
    def winner(self, sock: socket.socket, seq: int):
        return {
            "seq": seq
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