import pickle
import socket
from src.CryptoUtils import Ascrypt

def msg_sender(func):
    """
    Decorator to handle sending messages
    """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        private_key = args[-1]
        signature = Ascrypt.sign(private_key, pickle.dumps(res))
        msg = {
            "type": func.__name__,
            "data": res,
            "signature": signature
        }
        if args[1] is not None:
            args[0].send(args[1], pickle.dumps(msg))
        return msg
    return wrapper

# TODO: import this into the other files
def msg_receiver(func):
    """
    Decorator to handle receiving messages
    """
    def wrapper(*args, **kwargs):
        data = args[2]
        signature = args[3]
        public_key = args[4]
        func(*args, **kwargs)
        if Ascrypt.verify(public_key, pickle.dumps(data), signature):
            return func(*args, **kwargs)
        else:
            raise Exception("Invalid signature")
    return wrapper


class BingoProtocol:

    def __init__(self):
        pass

    @msg_sender
    def disqualify(self, sock: socket.socket, seq: int, reason: str, private_key):
        return {
            "seq": seq,
            "reason": reason
        }


    @msg_sender
    def get_logs(self, sock: socket.socket, private_key):
        return {}


    @msg_sender
    def logs_response(self, sock: socket.socket, logs: list, private_key):
        return {
            "logs": logs
        }


    @msg_sender
    def join(self, sock: socket.socket, cc, client: str, nickname: str, public_key: bytes, private_key): 
        return {
            "client": client,
            "nickname": nickname,
            "public_key": public_key
        }


    @msg_sender
    def join_response(self, sock: socket.socket, accepted: bool, sequence_number: int, private_key): 
        return {
            "accepted": accepted, 
            "seq": sequence_number
        }

    
    @msg_sender
    def start(self, sock: socket.socket, private_key):
        return {}

    
    @msg_sender
    def start_response(self, sock: socket.socket, num_players: int, private_key):
        return {
            "num_players": num_players
        }


    @msg_sender
    def card(self, sock: socket.socket, card: list, seq: int, private_key):
        return {
            "card": card,
            "seq": seq
        }


    @msg_sender
    def deck(self, sock: socket.socket, deck: list, seq: int, private_key):
        return {
            "deck": deck,
            "seq": seq
        }


    @msg_sender
    def final_deck(self, sock: socket.socket, deck: list, private_key):
        return {
            "deck": deck,
        }


    @msg_sender
    def key(self, sock: socket.socket, seq: int, key: bytes, private_key):
        return {
            "seq": seq,
            "key": key
        }


    @msg_sender
    def keys(self, sock: socket.socket, keys: dict, private_key):
        return {
            "keys": keys
        }


    @msg_sender
    def winners(self, sock: socket.socket, seq:int, winners: list, private_key):
        return {
            "seq": seq,
            "winners": winners
        }

    @msg_sender
    def final_winners(self, sock: socket.socket, winners: list, private_key):
        return {
            "winners": winners
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