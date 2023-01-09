import json
import socket
from src.CryptoUtils import Ascrypt, BytesSerializer
from src.CitizenCard import CitizenCard
import os
from dotenv import load_dotenv

load_dotenv()
USE_CARD = bool(int(os.getenv("USE_CARD")))

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
        if res["type"] == "join":
            if USE_CARD:
                cc_signature = args[2].sign(json.dumps(res).encode("utf-8"))
                msg["cc_signature"] = BytesSerializer.to_base64_str(cc_signature)
            parea_pub_key = args[-1]
            msg["data"]["public_key"] = Ascrypt.encrypt_to_str(parea_pub_key, msg["data"]["public_key"].encode("utf-8"))
            msg["data"]["cc_certificate"] = Ascrypt.encrypt_to_str(parea_pub_key, msg["data"]["cc_certificate"].encode("utf-8"))
        msg_bytes = json.dumps(msg).encode("utf-8")
        if args[1] is not None:
            args[0].send(args[1], msg_bytes)
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
        return {}


    @msg_sender
    def logs_response(self, sock: socket.socket, logs: list):
        return {
            "logs": logs
        }


    @msg_sender
    def get_parea_public_key(self, sock: socket.socket):
        return {}


    @msg_sender
    def parea_public_key_response(self, sock: socket.socket, parea_public_key: str):
        return {
            "parea_public_key": parea_public_key
        }


    @msg_sender
    def join(self, sock: socket.socket, cc: CitizenCard, client: str, nickname: str, public_key: str, parea_pub_key):
        return {
            "client": client,
            "nickname": nickname,
            "public_key": public_key,
            "cc_certificate": "CC_CERTIFICATE" if not USE_CARD else cc.export_cert()
        }


    @msg_sender
    def join_response(self, sock: socket.socket, accepted: bool, seq: int):
        return {
            "accepted": accepted, 
            "seq": seq,
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