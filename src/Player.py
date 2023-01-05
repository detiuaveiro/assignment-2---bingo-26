from src.User import User
from src.CryptoUtils import Scrypt, Ascrypt
import random

class Player(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as player
        self.proto.join(self.sock, self.cc, "player", nickname, Ascrypt.serialize_key(self.pub_key))

        self.handlers = {
            "join_response": self.handle_join_response,
            "start": self.handle_start,
            "card": self.handle_card
        }

        self.card = random.sample(range(0, 100), 25)
        # for i in range(len(self.card)):
        #     self.card[i] = Scrypt.encrypt(self.sym_key, self.iv, str(self.card[i]), "CBC")


    def handle_start(self, conn, data):
        self.proto.card(self.sock, self.card, self.seq)
