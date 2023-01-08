from src.User import User
from src.CryptoUtils import Ascrypt, Scrypt
import random
import time

class Caller(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as caller
        self.proto.join(self.sock, self.cc, "caller", nickname, Ascrypt.serialize_key(self.pub_key))

        self.deck = random.sample(range(0, 100), 100)
        self.handlers = {
            "logs_response": self.handle_logs_response,
            "join_response": self.handle_join_response,
            "ready_response": self.handle_ready_response,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "keys_response": self.handle_keys_response,
            "winners": self.handle_winners
        }

        # wait 30 seconds for players to join
        time.sleep(5)
        self.proto.ready(self.sock)
        print("Sent ready")
        # self.proto.start(self.sock)
        self.num_players = 0
        self.winners_recv = 0
        self.decks_recv = 0
        self.winners = []



    def handle_ready_response(self, conn, data: dict):
        print("Received ready response")
        self.players_info = data["players"]
        self.num_players = len(self.players_info)

        # TODO sign players_info

        players_info_signed = self.players_info
        self.proto.start(self.sock, players_info_signed)



    def handle_card(self, conn, data):
        print("Received card from player ", data["seq"])
        self.cards.append((data["card"], data["seq"]))

        if len(self.cards) == self.num_players:
            self.proto.deck(self.sock, self.deck)
        

        # print("Received card from ", data["seq"])
        # self.cards.append((data["card"], data["seq"]))
        # if len(self.cards) == self.num_players:

        #     # encrypt each number in deck with sym_key
        #     print("Original deck: ", self.deck)
        #     encrypted_deck = Scrypt.encrypt_list(self.deck, self.sym_key, self.iv, "CBC", True)
        #     self.proto.deck(self.sock, encrypted_deck, self.seq)



    def handle_deck(self, conn, data: dict):
        print("Received deck from player ", data["seq"])
        self.decks_recv += 1

        if self.decks_recv == self.num_players:
            final_deck = data["deck"] 
            # TODO signed deck
            self.proto.final_deck(self.sock, final_deck)
            self.proto.key(self.sock, ["key", "iv"])
            print("Sent final deck and key")



    def handle_keys_response(self, conn, data):
        print("Keys received")

        # TODO decrypt deck with keys

        self.winners = self.get_winners()
        print("Winners calculated")
        


    def handle_winners(self, conn, data):
        print("Received winners from ", data["seq"])
        # TODO verificar se está correto, senao banir
        self.winners_recv += 1
        if self.winners_recv == self.num_players:
            print("Winners: ", self.winners)
            self.proto.final_winners(self.sock, self.winners)
            print("Sent final winners")

