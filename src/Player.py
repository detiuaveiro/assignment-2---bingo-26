from src.User import User, M, N
from src.CryptoUtils import Scrypt, Ascrypt, BytesSerializer
import random
import sys
from dotenv import load_dotenv
import os

load_dotenv()
MISBEHAVE_PROBABILITY = float(os.getenv("MISBEHAVE_PROBABILITY"))

class C:
    RED = '\033[91m'       # error
    GREEN = '\033[92m'     # success
    YELLOW = '\033[93m'    # warning
    RESET = '\033[0m'      # reset

class Player(User):
    def __init__(self, nickname, parea_host, parea_port, pin, slot):
        super().__init__(nickname, parea_host, parea_port, pin, slot)

        self.handlers = {
            "parea_public_key_response": self.handle_parea_public_key_response,
            "redirect": self.handle_redirect,
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

    
        self.mb_card = False                # send wrong card format (invalid size, invalid numbers, repeated numbers)
        self.mb_wrong_seq = False           # send wrong seq inside the msg
        self.mb_invalid_sig = False         # send message with wrong signature 
        self.mb_send_final_winners = False  # any type without permission
        self.mb_send_2_cards = False        # send more than 1 card, deck, winners
        self.mb_wrong_winners = False       # send my seq as winner

        if random.random() < MISBEHAVE_PROBABILITY:
            num = random.randint(0, 5)
            if num == 0:
                self.mb_card = True
            elif num == 1:
                self.mb_wrong_seq = True
            elif num == 2:
                self.mb_invalid_sig = True
            elif num == 3:
                self.mb_send_final_winners = True
            elif num == 4:
                self.mb_send_2_cards = True
            elif num == 5:
                self.mb_wrong_winners = True

        self.proto.get_parea_public_key(self.sock)
        print("Parea public key requested")
            

    def handle_parea_public_key_response(self, conn, data, signature):
        print(f"{C.GREEN}Parea public key received{C.RESET}")
        # Join playing area as player
        self.proto.join(self.sock, self.cc, "player", self.nickname, Ascrypt.serialize_key(self.pub_key), self.parea_pub_key)



    def handle_start(self, conn, data, signature):
        self.players_info = data["players"]
        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()
        print("\n\nGame started")
        self.card = random.sample(range(0, M), N)

        if self.mb_card:
            print(f"{C.YELLOW}MISBEHAVING: Sending wrong card format{C.RESET}")
            self.card = self.card[:N-1]

        self.cards.append((self.card, self.seq))
        print("Card generated")
        print("My card: ", self.card)

        if self.mb_send_2_cards:
            print(f"{C.YELLOW}MISBEHAVING: Sending 2 cards{C.RESET}")
            self.proto.card(self.sock, self.card)

        if self.mb_wrong_seq:
            print(f"{C.YELLOW}MISBEHAVING: Sending wrong sequence number{C.RESET}")
            self.proto.seq = self.seq - 1

        if self.mb_invalid_sig:
            print(f"{C.YELLOW}MISBEHAVING: Sending invalid signature{C.RESET}")
            priv_key, _ = Ascrypt.generate_key_pair()
            self.proto.private_key = priv_key

        self.proto.card(self.sock, self.card)
        print("Card sent")



    def handle_join_response(self, conn, data, signature):
        if data["accepted"]:
            print("Joined playing area")
            self.seq = data["seq"]
            self.proto.seq = self.seq
            print("My sequence number:", self.seq)
        else:
            print("Join request denied")
            exit(0)



    def handle_card(self, conn, data, signature):
        print("Received card from ", data["seq"])
        self.cards.append((data["card"], data["seq"]))



    def handle_deck(self, conn, data, signature):
        print("Deck received from ", data["seq"])
        encrypted_deck = Scrypt.encrypt_list(data["deck"], self.sym_key, self.iv, "CBC")
        random.shuffle(encrypted_deck)
        print("Deck encrypted and shuffled")
        self.proto.deck(self.sock, encrypted_deck)
 


    def handle_final_deck(self, conn, data, signature):
        print("Final deck received from caller")
        self.deck = data["deck"]
        self.proto.key(self.sock, [BytesSerializer.to_base64_str(self.sym_key), BytesSerializer.to_base64_str(self.iv)])
        print("Key sent")



    def handle_keys_response(self, conn, data, signature):
        print("Keys received")
        # decrypt deck
        keys = data["keys"]
        for k, iv in keys[:-1]:
            k = BytesSerializer.from_base64_str(k)
            iv = BytesSerializer.from_base64_str(iv)
            self.deck = Scrypt.decrypt_list(self.deck, k, iv, "CBC", False)
        last_key = BytesSerializer.from_base64_str(keys[-1][0])
        last_iv = BytesSerializer.from_base64_str(keys[-1][1])
        self.deck = Scrypt.decrypt_list(self.deck, last_key, last_iv, "CBC")  # for the last key we must convert to int
        print("Deck decrypted: ", self.deck)
        winners = self.get_winners()

        if self.mb_send_final_winners:
            print(f"{C.YELLOW}MISBEHAVING: Sending final winners{C.RESET}")
            self.proto.final_winners(self.sock, [self.seq])

        if self.mb_wrong_winners:
            print(f"{C.YELLOW}MISBEHAVING: Sending wrong winners{C.RESET}")
            winners = [self.seq]

        self.proto.winners(self.sock, winners)
        print("Winners calculated and sent")



    def handle_final_winners(self, conn, data, signature):
        print("Final winners received from caller")
        print("Winners: ", data["winners"])
        self.options()



    def options(self):
        self.seq = None
        self.cards = []
        self.deck = []
        self.players_info = {}
        self.playing = False
        self.card = None
        print("\nNew game\n")
        print(
            "Options:\n\
            1 - Play again\n\
            2 - Show logs\n\
            3 - Exit"
        )
        print("Response: ", end="")
        sys.stdout.flush()

    
    def handle_input(self, command):
        if self.playing:
            return

        if command == "1":
            self.priv_key, self.pub_key = Ascrypt.generate_key_pair()
            self.proto.private_key = self.priv_key
            self.proto.join(self.sock, self.cc, "player", self.nickname, Ascrypt.serialize_key(self.pub_key), self.parea_pub_key)
        elif command == "2":
            self.proto.get_logs(self.sock)
            print("Sent logs request")
        elif command == "3":
            exit(0)


    def handle_exception(self, e, data):
        print("Invalid message received")
        # print("Error:", e)
        # print("Data:", data)
