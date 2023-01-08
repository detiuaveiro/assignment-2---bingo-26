from src.User import User
from src.CryptoUtils import Scrypt, Ascrypt
import random

class Player(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as player
        self.proto.join(self.sock, self.cc, "player", nickname, Ascrypt.serialize_key(self.pub_key))

        self.handlers = {
            "disqualify": self.handle_disqualify,
            "logs_response": self.handle_logs_response,
            "join_response": self.handle_join_response,
            "start": self.handle_start,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "final_deck": self.handle_final_deck,
            "keys_response": self.handle_keys_response,
            "final_winners": self.handle_final_winners
        }

        self.card = None


    def handle_disqualify(self, conn, data):
        pass



    def handle_start(self, conn, data):

        # TODO gerar chaves simetricas

        print("Game started")
        self.card = random.sample(range(0, 100), 25)
        self.cards.append((self.card, self.seq))
        print("Card generated")
        self.proto.card(self.sock, self.card)
        print("Card sent")



    def handle_card(self, conn, data):
        print("Received card from ", data["seq"])
        self.cards.append((data["card"], data["seq"]))



    def handle_deck(self, conn, data):
        print("Deck received from ", data["seq"])
        deck = data["deck"]
        random.shuffle(deck)

        # TODO encrypt deck
        
        self.proto.deck(self.sock, deck)
 


    def handle_final_deck(self, conn, data):
        print("Final deck received from caller")
        self.deck = data["deck"]
        # TODO send key and iv
        self.proto.key(self.sock, ["key", "iv"])
        print("Key sent")



    def handle_keys_response(self, conn, data):
        print("Keys received")

        # TODO decrypt deck

        winners = self.get_winners()
        self.proto.winners(self.sock, winners)
        print("Winners calculated and sent")



    def handle_final_winners(self, conn, data):
        print("Final winners received from caller")
        print("Winners: ", data["winners"])
