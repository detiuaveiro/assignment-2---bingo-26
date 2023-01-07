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
            "deck": self.handle_deck,
            "final_deck": self.handle_final_deck,
            "keys": self.handle_keys,
            "final_winners": self.handle_final_winners
        }

        self.card = random.sample(range(0, 100), 25)


    def handle_start(self, conn, data):
        print("Game started")
        self.proto.card(self.sock, self.card, self.seq)
        print("Card sent")

    
    def handle_card(self, conn, data):
        print("Received card from ", data["seq"])
        self.cards.append((data["card"], data["seq"]))


    def handle_deck(self, conn, data):
        print("Deck received from ", data["seq"])
        encrypted_deck = Scrypt.encrypt_list(data["deck"], self.sym_key, self.iv, "CBC", False)
        random.shuffle(encrypted_deck)
        print("Deck encrypted and shuffled")
        self.proto.deck(self.sock, encrypted_deck, self.seq)
        
        
        # print("Deck received from ", data["seq"])
        # deck = data["deck"]
        # random.shuffle(deck)
        # self.proto.deck(self.sock, deck, self.seq)
        # print("Deck shuffled and sent")

        # print("\n\nWinner:")
        # print(list(self.get_winners())[0])



    def handle_final_deck(self, conn, data):
        print("Final deck received from caller")
        self.deck = data["deck"]
        self.proto.key(self.sock, self.seq, (self.sym_key, self.iv))
        print("Key sent")


    def handle_keys(self, conn, data):
        print("Keys received")

        # decrypt deck
        keys = data["keys"]
        for k, iv in keys[:-1]:
            self.deck = Scrypt.decrypt_list(self.deck, k, iv, "CBC", False)
        self.deck = Scrypt.decrypt_list(self.deck, keys[-1][0], keys[-1][1], "CBC", True)  # for the last key we must convert to int
        print("Deck decrypted: ", self.deck)

        # calculate winner
        winners = self.get_winners()
        print("Winners calculated")
        self.proto.winners(self.sock, self.seq, winners)


    def handle_final_winners(self, conn, data):
        print("Final winners received from caller")
        print("Winners: ", data["winners"])

        
        
