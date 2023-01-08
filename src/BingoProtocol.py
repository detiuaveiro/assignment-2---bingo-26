import json
import socket
from src.CryptoUtils import Ascrypt, BytesSerializer

def msg_sender(func):
    """
    Decorator to handle sending messages
    """
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        res["type"] = func.__name__
        signature = Ascrypt.sign(args[0].private_key, json.dumps(res).encode("utf-8"))
        msg = {
            "data": res,
            "signature": BytesSerializer.to_base64_str(signature)
        }
        if args[1] is not None:
            args[0].send(args[1], json.dumps(msg).encode('utf-8'))
        return msg
    return wrapper


class BingoProtocol:

    def __init__(self, private_key: bytes):
        self.seq = None
        self.private_key = private_key


    @msg_sender
    def redirect(self, sock: socket.socket, data: dict, signature: str):
        return {
            "msg": {
                "data": data,
                "signature": signature
            }
        }


    @msg_sender
    def disqualify(self, sock: socket.socket, target_seq: int, reason: str):
        return {
            "seq": self.seq,
            "target_seq": target_seq,
            "reason": reason
        }


    @msg_sender
    def get_logs(self, sock: socket.socket):
        return {
            "seq": self.seq
        }


    @msg_sender
    def logs_response(self, sock: socket.socket, logs: list):
        return {
            "logs": logs
        }


    @msg_sender
    def join(self, sock: socket.socket, cc, client: str, nickname: str, public_key: str): 
        return {
            "client": client,
            "nickname": nickname,
            "public_key": public_key
        }


    @msg_sender
    def join_response(self, sock: socket.socket, accepted: bool, seq: int, parea_public_key: str):
        return {
            "accepted": accepted, 
            "seq": seq,
            "parea_public_key": parea_public_key
        }


    @msg_sender
    def ready(self, sock: socket.socket):
        return {
            "seq": self.seq
        }

    
    @msg_sender
    def ready_response(self, sock: socket.socket, players: list):
        return {
            "players": players
        }
    

    @msg_sender
    def start(self, sock: socket.socket, players: dict):
        return {
            "seq": self.seq,
            "players": players
        }



    @msg_sender
    def card(self, sock: socket.socket, card: list):
        return {
            "seq": self.seq,
            "card": card,
        }


    @msg_sender
    def deck(self, sock: socket.socket, deck: list):
        return {
            "seq": self.seq,
            "deck": deck,
        }


    @msg_sender
    def final_deck(self, sock: socket.socket, deck: list):
        return {
            "seq": self.seq,
            "deck": deck,
        }


    @msg_sender
    def key(self, sock: socket.socket, key: list[str, str]):
        return {
            "seq": self.seq,
            "key": key
        }


    @msg_sender
    def keys_response(self, sock: socket.socket, keys: list):
        return {
            "keys": keys
        }


    @msg_sender
    def winners(self, sock: socket.socket, winners: list):
        return {
            "seq": self.seq,
            "winners": winners
        }


    @msg_sender
    def final_winners(self, sock: socket.socket, winners: list):
        return {
            "seq": self.seq,
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
            return json.loads(msg.decode('utf-8'))