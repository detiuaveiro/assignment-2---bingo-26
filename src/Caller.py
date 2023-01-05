from src.User import User
from src.CryptoUtils import Ascrypt
import random
import time

class Caller(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as caller
        self.proto.join(self.sock, self.cc, "caller", nickname, Ascrypt.serialize_key(self.pub_key))

        self.deck = random.sample(range(0, 100), 100)
        self.handlers = {
            "join_response": self.handle_join_response,
            "start": self.handle_start,
            "start_response": self.handle_start_response,
            "card": self.handle_card
        }

        # wait 30 seconds for players to join
        time.sleep(30)
        self.proto.start(self.sock)

        self.num_players = 0


    def handle_start(self, conn, data):
        print("Game started!")
       

    def handle_start_response(self, conn, data):
        self.num_players = data["num_players"]


    def handle_card(self, conn, data):
        self.cards.append((data["card"], data["seq"]))
        if len(self.cards) == self.num_players:
            self.proto.deck(self.sock, self.deck)       
