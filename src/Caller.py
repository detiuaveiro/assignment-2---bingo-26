from src.User import User, N, M
from src.CryptoUtils import Ascrypt, Scrypt, BytesSerializer
import random

class Caller(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as caller
        self.proto.join(self.sock, self.cc, "caller", nickname, Ascrypt.serialize_key(self.pub_key))

        self.handlers = {
            "redirect": self.handle_redirect,
            "logs_response": self.handle_logs_response,
            "join_response": self.handle_join_response,
            "ready_response": self.handle_ready_response,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "keys_response": self.handle_keys_response,
            "winners": self.handle_winners
        }

        self.deck = []
        self.num_players = 0
        self.winners_recv = 0
        self.decks_recv = 0
        self.winners = []



    def handle_ready_response(self, conn, data, signature):
        print("Received ready response")
        self.players_info = {str(p[0]): (p[1], p[2]) for p in data["players"]}
        self.num_players = len(self.players_info) - 1
        self.proto.start(self.sock, self.players_info)
        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()



    def handle_card(self, conn, data, signature):
        print("Received card from player ", data["seq"])

        # TODO verificar card (cheating)

        self.cards.append((data["card"], data["seq"]))
        if len(self.cards) == self.num_players:
            self.deck = random.sample(range(0, M), M)
            print("Original deck: ", self.deck)
            encrypted_deck = Scrypt.encrypt_list(self.deck, self.sym_key, self.iv, "CBC")
            self.proto.deck(self.sock, encrypted_deck)


    def handle_deck(self, conn, data, signature):
        print("Received deck from player ", data["seq"])
        self.deck = data["deck"]
        self.decks_recv += 1

        if self.decks_recv == self.num_players:
            final_deck = data["deck"] 
            self.proto.final_deck(self.sock, final_deck)
            self.proto.key(self.sock, [BytesSerializer.to_base64_str(self.sym_key), BytesSerializer.to_base64_str(self.iv)])
            print("Sent final deck and key")



    def handle_keys_response(self, conn, data, signature):
        print("Keys received")
        keys = data["keys"]
        for k, iv in keys[:-1]:
            k = BytesSerializer.from_base64_str(k)
            iv = BytesSerializer.from_base64_str(iv)
            self.deck = Scrypt.decrypt_list(self.deck, k, iv, "CBC", False)
        last_key = BytesSerializer.from_base64_str(keys[-1][0])
        last_iv = BytesSerializer.from_base64_str(keys[-1][1])
        self.deck = Scrypt.decrypt_list(self.deck, last_key, last_iv, "CBC")  # for the last key we must convert to int
        print("Deck decrypted: ", self.deck)
        self.winners = self.get_winners()
        print("Winners calculated")
        


    def handle_winners(self, conn, data, signature):
        print("Received winners from ", data["seq"])
        # TODO verificar se está correto, senao banir
        self.winners_recv += 1
        if self.winners_recv == self.num_players:
            print("Winners: ", self.winners)
            self.proto.final_winners(self.sock, self.winners)
            print("Sent final winners")
            exit(0)


    def handle_input(self, command):
        self.proto.ready(self.sock)
        print("Sent ready")