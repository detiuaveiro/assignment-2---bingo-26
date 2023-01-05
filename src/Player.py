from src.User import User
from src.CryptoUtils import Scrypt
import random

class Player(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)
        # Join playing area as player
        self.proto.join(self.sock, self.cc, "player")

        self.handlers = {
            "join_response": self.handle_join_response,
        }

        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()
        self.card = random.sample(range(0, 100), 25)
        for i in range(len(self.card)):
            self.card[i] = Scrypt.encrypt(self.sym_key, self.iv, str(self.card[i]), "CBC")