import socket
import selectors
from src.BingoProtocol import BingoProtocol
# from src.CitizenCard import CitizenCard
from src.CryptoUtils import Ascrypt, Scrypt

class User:
    def __init__(self, nickname, parea_host, parea_port, pin):
        self.nickname = nickname
        self.seq = None
        self.cards = []

        # proto
        self.proto = BingoProtocol()
        
        self.parea_host = parea_host
        self.parea_port = parea_port
        #socket and selector
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # connect to playing area
        self.sock.connect((self.parea_host, self.parea_port))
        self.sel.register(self.sock, selectors.EVENT_READ, self.read)

        # symetric emcryption
        self.sym_key = Scrypt.generate_symmetric_key()
        self.iv = Scrypt.generate_iv()

        # asymmetric encryption
        self.priv_key, self.pub_key = Ascrypt.generate_key_pair()
        
        # cc
        self.cc = None # replace by CitizenCard(pin)


    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            print("Received:", data)
            try:
                self.handlers[data["type"]](conn, data["data"])
            except Exception as e:
                print("Invalid message received")
                print("Error:", e)
                exit(1)
        else:
            print("Connection closed by playing area:", conn.getpeername())
            self.sel.unregister(conn)
            conn.close()
            exit(0)


    def handle_join_response(self, conn: socket.socket, data: dict):
        if data["accepted"]:
            print("Joined playing area")
            self.seq = data["seq"] # sequence number
        else:
            print("Join request denied")
            self.sel.unregister(self.sock)
            self.sock.close()
            exit(0)


    def handle_card(self, conn: socket.socket, data: dict):
        print(f"Received card from {data['seq']} {data['card']}")
        #check of card is valid: TODO


    def get_winners(self):
        win_pos = []
        for card, seq in self.cards:
            for idx in range(25, len(self.deck)+1):
                card_set = set(card)
                deck_set = set(self.deck[:idx])
                if card_set.issubset(deck_set):
                    win_pos.append((seq, idx))
                    break
        win_pos.sort(key=lambda x: x[1])
        winners = set()
        for winner in win_pos:
            if winner[1] == win_pos[0][1]:
                winners.add(winner[0])
            else:
                break


    def run(self):
        while True:
            events = self.sel.select(0)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)