from src.User import User
from src.CryptoUtils import Ascrypt, Scrypt
import random
import time

class Caller(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as caller
        self.proto.join(self.sock, self.cc, "caller", nickname, Ascrypt.serialize_key(self.pub_key), self.priv_key)

        self.deck = random.sample(range(0, 100), 100)
        self.handlers = {
            "join_response": self.handle_join_response,
            "start": self.handle_start,
            "start_response": self.handle_start_response,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "keys": self.handle_keys,
            "winners": self.handle_winners
        }

        # wait 30 seconds for players to join
        time.sleep(20)
        self.proto.start(self.sock, self.priv_key)
        self.num_players = 0
        self.winners_recv = 0
        self.winners = []


    def handle_start(self, conn, data):
        print("Game started!")
       

    def handle_start_response(self, conn, data):
        self.num_players = data["num_players"]


    def handle_card(self, conn, data):
        print("Received card from ", data["seq"])
        self.cards.append((data["card"], data["seq"]))
        if len(self.cards) == self.num_players:

            # encrypt each number in deck with sym_key
            print("Original deck: ", self.deck)
            encrypted_deck = Scrypt.encrypt_list(self.deck, self.sym_key, self.iv, "CBC", True)
            self.proto.deck(self.sock, encrypted_deck, self.seq, self.priv_key)


    def handle_deck(self, conn, data: dict):
        print("Received last deck")
        self.deck = data["deck"]

        # TODO sign deck
        self.proto.final_deck(self.sock, self.deck, self.priv_key)
        self.proto.key(self.sock, self.seq, (self.sym_key, self.iv), self.priv_key)
        print("Sent final deck and key")


    def handle_keys(self, conn, data):
        print("Received keys")

        # decrypt deck
        keys = data["keys"]
        for k, iv in keys[:-1]:
            self.deck = Scrypt.decrypt_list(self.deck, k, iv, "CBC", False)
        self.deck = Scrypt.decrypt_list(self.deck, keys[-1][0], keys[-1][1], "CBC", True)  # for the last key we must convert to int
        print("Deck decrypted: ", self.deck)
        
        # calculate winner
        self.winners = self.get_winners()
        print("Winners calculated")


    def handle_winners(self, conn, data):
        print("Received winners from ", data["seq"])
        # TODO verificar se está correto
        self.winners_recv += 1
        if self.winners_recv == self.num_players:
            print("Winners: ", self.winners)
            self.proto.final_winners(self.sock, self.winners, self.priv_key)
            print("Sent final winners")

