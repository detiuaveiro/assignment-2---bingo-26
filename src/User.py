import socket
import selectors
from src.BingoProtocol import BingoProtocol
# from src.CitizenCard import CitizenCard
from src.CryptoUtils import Ascrypt, Scrypt, BytesSerializer
import json

import sys      # for non-blocking input
import fcntl    # for non-blocking input
import os       # for non-blocking input

class User:
    def __init__(self, nickname, parea_host, parea_port, pin):
        self.nickname = nickname
        self.pin = pin
        self.seq = None
        self.cards = []
        self.deck = []
        self.players_info = []

        # proto
        self.proto = BingoProtocol("PRIVATE_KEY")
        
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
        self.sym_key = None
        self.iv = None

        # asymmetric encryption
        self.priv_key, self.pub_key = Ascrypt.generate_key_pair()
        
        # cc
        self.cc = None # replace by CitizenCard(pin)

        ## non-blocking input
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data)


    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            try:
                if data["type"] == "join_response":
                    self.parea_pub_key = Ascrypt.deserialize_key(data["data"]["public_key"])
                # TODO self.verify_signature(data)

                self.handlers[data["data"]["type"]](conn, data["data"], data["signature"])
            except Exception as e:
                print("Invalid message received")
                print("Error:", e)
                exit(1)
        else:
            print("Connection closed by playing area:", conn.getpeername())
            self.sel.unregister(conn)
            conn.close()
            exit(0)



    def verify_signature(self, data):
        content = json.dumps(data["data"]).encode("utf-8")
        signature = BytesSerializer.from_base64_str(data["signature"])
        if not Ascrypt.verify(self.parea_pub_key, content, signature):
            print("\033[91mInvalid signature")
            raise Exception("Invalid signature")



    def handle_redirect(self, conn, data, signature):
        msg = data["msg"]
        # TODO check signature
        self.handlers[msg["data"]["type"]](conn, msg["data"], msg["signature"])



    def handle_join_response(self, conn, data, signature):
        if data["accepted"]:
            print("Joined playing area")
            self.seq = data["seq"]
            self.proto.seq = self.seq
            print("My seq:", self.seq)
        else:
            print("Join request denied")
            self.sel.unregister(self.sock)
            self.sock.close()
            exit(0)



    def handle_logs_response(self, conn, data):
        pass
    


    def get_winners(self):
        win_pos = []
        for card, seq in self.cards:
            counter = 0
            for idx, num in enumerate(self.deck):
                if num in card:
                    counter += 1
                if counter == 25:
                    win_pos.append((seq, idx))
                    break
        win_pos.sort(key=lambda x: (x[1], x[0]))
        winners = []
        for winner in win_pos:
            if winner[1] == win_pos[0][1]:
                winners.append(winner[0])
            else:
                break
        return winners


    def got_keyboard_data(self, stdin, mask):
        command = stdin.read().strip()
        self.handle_input(command)


    def run(self):
        while True:
            events = self.sel.select(0)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)