import socket
import selectors
from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Ascrypt



def player_check(func):
    def wrapper(self, conn: socket.socket, data: dict):
        if conn in self.players:
            func(self, conn, data)
        else:
            print("Invalid message received")
            self.close_conn(conn)
    return wrapper



def caller_check(func):
    def wrapper(self, conn: socket.socket, data: dict):
        if conn in self.caller:
            func(self, conn, data)
        else:
            print("Invalid message received")
            self.close_conn(conn)
    return wrapper



def user_check(func):
    def wrapper(self, conn: socket.socket, data: dict):
        if conn in self.players or conn in self.caller:
            func(self, conn, data)
        else:
            print("Invalid message received")
            self.close_conn(conn)
    return wrapper



class PlayingArea:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)

        self.proto = BingoProtocol()
        self.users_by_seq = {}        # {seq: conn}
        self.players = {}               # {conn: (seq, nickname, public_key)}
        self.caller = {}                # {conn: (seq, nickname, public_key)}
        self.current_id = 0
        self.total_shuffles = 0
        self.playing = False            # blocks new players from joining
        self.checking_winner = False    # blocks new cards from being played
        self.deck = []
        self.all_msgs = []

        # asymmetric encryption
        self.private_key, self.public_key = Ascrypt.generate_key_pair()

        self.handlers = { 
            "join": self.handle_join,
            "start": self.handle_start,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "winner": self.handle_winner,
        }



    def handle_join(self, conn: socket.socket, data: dict):
        if data["client"] == "player":
            self.current_id += 1
            self.proto.join_response(conn, not self.playing, self.current_id)
            if not self.playing:
                self.players[conn] = (self.current_id, data["nickname"], data["public_key"])
                self.users_by_seq[self.current_id] = conn
                print("Player joined playing area")
            else:
                print("Join request denied")
                self.close_conn(conn)
        elif data["client"] == "caller":
            self.proto.join_response(conn, len(self.caller) == 0, 0)
            if len(self.caller) == 0:
                self.caller[conn] = (0, data["nickname"], data["public_key"])
                self.users_by_seq[0] = conn
                print("Caller joined playing area")
            else:
                print("Join request denied, caller already exists")
                self.close_conn(conn)
        else:
            self.proto.join_response(conn, False)
            print("Join request denied, unknown client")
            self.close_conn(conn)



    @caller_check
    def handle_start(self, conn: socket.socket, data: dict):
        for c in self.other_conns(conn):
            self.proto.start(c)
        self.playing = True
        self.proto.start_response(conn, len(self.players))



    @player_check
    def handle_card(self, conn: socket.socket, data: dict):
        for c in self.other_conns(conn):
            self.proto.card(c, data["card"], data["seq"])



    @caller_check
    def handle_deck(self, conn: socket.socket, data: dict):
        # #commit deck
        # self.deck = data["deck"]

        # if self.total_shuffles < len(self.players):
        #     self.proto.deck(self.users_by_seq[self.total_shuffles + 1], self.deck, data["seq"])
        #     self.total_shuffles += 1

        #     if self.total_shuffles == len(self.players):
        #         self.proto.deck(self.users_by_seq[0], self.deck, data["seq"]) #send deck to caller
                
        # else:
        #     # notify users to give its sym priv key
        #     print("Asking for sym priv key")

        for c in self.other_conns(conn):
            self.proto.deck(c, data["deck"], data["seq"])

    

    @user_check
    def handle_winner(self, conn: socket.socket, data: dict):
        for c in self.other_conns(conn):
            self.proto.winner(c, data["winner"])



    def accept(self, sock, mask):
        conn, addr = sock.accept()
        print("Trying to join playing area: ", addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)



    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            print("Received:", data)
            # try:
            self.handlers[data["type"]](conn, data["data"])
            # except Exception as e:
            #     print("Invalid message received")
            #     print("Error:", e)
            #     exit(1)
        else:
            self.close_conn(conn)

    

    def close_conn(self, conn: socket.socket):
        if conn in self.players:
            print("Connection closed player: ", conn.getpeername())
            del self.users_by_seq[self.players[conn][0]]
            del self.players[conn]
        if conn in self.caller:
            print("Connection closed caller: ", conn.getpeername())
            del self.caller[conn]
        self.sel.unregister(conn)
        conn.close()



    def other_conns(self, conn: socket.socket):
        for c in self.players:
            if c != conn:
                yield c
        for c in self.caller:
            if c != conn:
                yield c



    def run(self):
        """ Run until canceled """
        while True:
            events = self.sel.select(0) 
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)