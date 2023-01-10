from src.User import User, N, M, BingoException
from src.CryptoUtils import Ascrypt, Scrypt, BytesSerializer
import random
import sys
import os
from dotenv import load_dotenv

load_dotenv()
MISBEHAVE_PROBABILITY = float(os.getenv("MISBEHAVE_PROBABILITY"))
if MISBEHAVE_PROBABILITY > 0: MISBEHAVE_PROBABILITY += 0.1 # more probable than Player cheats


class C:
    RED = '\033[91m'       # error
    GREEN = '\033[92m'     # success
    YELLOW = '\033[93m'    # warning
    RESET = '\033[0m'      # reset

def check_playing(func):
    def wrapper(self, *args, **kwargs):
        if self.playing:
            return func(self, *args, **kwargs)
        return
    return wrapper


class Caller(User):
    def __init__(self, nickname, parea_host, parea_port, pin, slot):
        super().__init__(nickname, parea_host, parea_port, pin, slot)

        self.handlers = {
            "parea_public_key_response": self.handle_parea_public_key_response,
            "redirect": self.handle_redirect,
            "disqualify": self.handle_disqualify,
            "logs_response": self.handle_logs_response,
            "join_response": self.handle_join_response,
            "ready_response": self.handle_ready_response,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "keys_response": self.handle_keys_response,
            "winners": self.handle_winners
        }

        self.num_players = 0
        self.winners_recv = 0
        self.decks_recv = 0
        self.winners = []

        self.cards_by_seq = []
        self.decks_by_seq = []
        self.winners_by_seq = []

        self.mb_wrong_winner = False        # send seq = 1 as winner
        self.mb_wrong_disqualify = False    # disqualify seq = 1 without him misbehave

        if random.random() < MISBEHAVE_PROBABILITY:
            num = random.randint(0, 1)
            if num == 0:
                self.mb_wrong_winner = True
            elif num == 1:
                self.mb_wrong_disqualify = True

        self.proto.get_parea_public_key(self.sock)
        print("Parea public key requested")


    
    def handle_parea_public_key_response(self, conn, data, signature):
        print(f"{C.GREEN}Parea public key received{C.RESET}")
        # Join playing area as player
        self.proto.join(self.sock, self.cc, "caller", self.nickname, Ascrypt.serialize_key(self.pub_key), self.parea_pub_key)



    def handle_join_response(self, conn, data, signature):
        if data["accepted"]:
            print("Joined playing area")
            self.seq = data["seq"]
            self.proto.seq = self.seq
            print("My sequence number:", self.seq)
            self.options()
        else:
            print("Join request denied")
            exit(0)



    def handle_ready_response(self, conn, data, signature):
        print("Received ready response")
        if len(data["players"]) <= 1:
            print("No players in playing area")
            self.options()
            return
        self.players_info = {str(p[0]): (p[1], p[2]) for p in data["players"]}
        self.num_players = len(self.players_info) - 1
        self.proto.start(self.sock, self.players_info)
        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()


    @check_playing
    def handle_card(self, conn, data, signature):
        print("Received card from player ", data["seq"])
        self.verify_card(data["card"], data["seq"])
        self.cards.append((data["card"], data["seq"]))
        if len(self.cards) == self.num_players:
            self.deck = random.sample(range(0, M), M)
            print("Original deck: ", self.deck)
            encrypted_deck = Scrypt.encrypt_list(self.deck, self.sym_key, self.iv, "CBC")
            self.proto.deck(self.sock, encrypted_deck)



    def verify_card(self, card, seq):
        if seq in self.cards_by_seq:
            raise BingoException("Player already sent a card")
        self.cards_by_seq.append(seq)
        if len(set(card)) != N:
            raise BingoException("Invalid card")
        for i in card:
            if i < 0 or i >= M:
                raise BingoException("Invalid card number")


    @check_playing
    def handle_deck(self, conn, data, signature):
        print("Received deck from player ", data["seq"])
        self.verify_deck(self.deck, data["seq"])
        self.deck = data["deck"]
        self.decks_recv += 1
        if self.decks_recv == self.num_players:
            final_deck = data["deck"] 
            self.proto.final_deck(self.sock, final_deck)
            self.proto.key(self.sock, [BytesSerializer.to_base64_str(self.sym_key), BytesSerializer.to_base64_str(self.iv)])
            print("Sent final deck and key")



    def verify_deck(self, deck, seq):
        if self.deck is None:
            raise BingoException("Player sent deck before caller")
        if seq in self.decks_by_seq:
            raise BingoException("Player already sent a deck")
        self.decks_by_seq.append(seq)
        if len(set(deck)) != M:
            raise BingoException("Invalid deck")


    @check_playing
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
        

    @check_playing
    def handle_winners(self, conn, data, signature):
        print("Received winners from ", data["seq"])
        self.verify_winners(data["winners"], data["seq"])
        self.winners_recv += 1
        if self.winners_recv == self.num_players:

            if self.mb_wrong_winner:
                print(f"{C.YELLOW}Misbehaving: sending wrong winners{C.RESET}")
                self.winners= [1]

            if self.mb_wrong_disqualify:
                print(f"{C.YELLOW}Misbehaving: disqualifying player 1 for Invalid winners{C.RESET}")
                self.proto.disqualify(self.sock, 1, "Invalid winners")
                self.playing = False

            print("Winners: ", self.winners)
            self.proto.final_winners(self.sock, self.winners)
            print("Sent final winners")
            self.options()



    def verify_winners(self, winners, seq):
        if seq in self.winners_by_seq:
            raise BingoException("Player already sent winners")
        self.winners_by_seq.append(seq)
        if winners != self.winners:
            raise BingoException("Invalid winners")



    def options(self):
        self.deck = []
        self.num_players = 0
        self.winners_recv = 0
        self.decks_recv = 0
        self.winners = []
        self.cards = []
        self.deck = []
        self.players_info = {}
        self.playing = False
        self.cards_by_seq = []
        self.decks_by_seq = []
        self.winners_by_seq = []
        print("\nNew game\n")
        print("Options:\n\
            1 - Start game\n\
            2 - Show logs\n\
            3 - Exit"
        )
        print("Response: ", end="")
        sys.stdout.flush()


    def handle_input(self, command):
        if self.playing:
            return

        if command == "1":
            self.proto.ready(self.sock)
            print("Sent ready")
            self.playing = True
        elif command == "2":
            self.proto.get_logs(self.sock)
            print("Sent logs request")
        elif command == "3":
            exit(0)


    def handle_exception(self, e, data):
        if isinstance(e, BingoException):
            reason = str(e)
        else:
            reason = "Invalid message received"
        taget_seq = data["data"]["msg"]["data"]["seq"]
        print(f"Disqualifying player {taget_seq} for {reason}")
        self.proto.disqualify(self.sock, taget_seq, reason)
        self.playing = False