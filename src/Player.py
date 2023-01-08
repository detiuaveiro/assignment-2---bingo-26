from src.User import User
from src.CryptoUtils import Scrypt, Ascrypt, BytesSerializer
import random

class Player(User):
    def __init__(self, nickname, parea_host, parea_port, pin):
        super().__init__(nickname, parea_host, parea_port, pin)

        # Join playing area as player
        self.proto.join(self.sock, self.cc, "player", nickname, Ascrypt.serialize_key(self.pub_key))

        self.handlers = {
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


    def handle_disqualify(self, conn, data, signature):
        if data["target_seq"] == self.seq:
            print("Disqualified for : ", data["reason"])
            exit(0)
        else:
            print(f"Player {data['target_seq']} disqualified for : ", data["reason"])



    def handle_start(self, conn, data, signature):
        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()
        print("\n\nGame started")
        self.card = random.sample(range(0, 100), 25)
        self.cards.append((self.card, self.seq))
        print("Card generated")
        print("My card: ", self.card)
        self.proto.card(self.sock, self.card)
        print("Card sent")



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
        self.proto.winners(self.sock, winners)
        print("Winners calculated and sent")



    def handle_final_winners(self, conn, data, signature):
        print("Final winners received from caller")
        print("Winners: ", data["winners"])
        exit(0)

    
    def handle_input(self, command):
        # TODO
        pass
