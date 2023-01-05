from src.User import User
from src.CryptoUtils import Scrypt
import random

class Player(User):
    def __init__(self, nickname, parea_host, parea_port):
        super().__init__(nickname, parea_host, parea_port)
        # Join playing area as player
        self.proto.join(self.sock, "player")

        self.handlers = {
            "join_response": self.handle_join_response,
        }

        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()
        self.card = random.sample(range(0, 100), 25)
        self.card = Scrypt.encrypt(self.sym_key, self.iv, self.card)