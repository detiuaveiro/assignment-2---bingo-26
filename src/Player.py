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
            "card": self.handle_card,
            "deck": self.handle_deck
        }

        self.card = random.sample(range(0, 100), 25)


    def handle_start(self, conn, data):
        self.proto.card(self.sock, self.card, self.seq)


    def handle_deck(self, conn, data: dict):
        self.deck = data["deck"]
        print("\n\nWinner:")
        print(list(self.get_winners())[0])

        # print("Deck received from ", data["seq"])
        # encrypted_deck = Scrypt.encrypt_list(data["deck"], self.sym_key, self.iv, "CBC", False)
        # random.shuffle(encrypted_deck)
        # print("Deck encrypted and shuffled")
        # self.proto.deck(self.sock, encrypted_deck, self.seq)
