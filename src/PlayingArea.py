import socket
import selectors
from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Ascrypt




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

        self.proto = BingoProtocol("PRIVATE_KEY")
        self.users_by_seq = {}        # {seq: conn}
        self.users = {}               # {conn: (seq, nickname, public_key)}
        self.caller = None
        self.current_id = 0
        self.total_shuffles = 0
        self.all_keys = {}
        self.playing = False            # blocks new players from joining
        self.all_msgs = []

        # asymmetric encryption
        self.private_key, self.public_key = Ascrypt.generate_key_pair()

        self.handlers = { 
            "disqualify": self.handle_disqualify,
            "get_logs": self.handle_get_logs,
            "join": self.handle_join,
            "ready": self.handle_ready,
            "start": self.handle_start,
            "card": self.handle_card,
            "deck": self.handle_deck,
            "final_deck": self.handle_final_deck,
            "key": self.handle_key,
            "winners": self.handle_winners,
            "final_winners": self.handle_final_winners
        }



    def handle_disqualify(self, conn, data, signature):
        pass



    def handle_get_logs(self, conn, data, signature):
        pass



    def handle_join(self, conn, data, signature):
        if data["client"] == "player":
            self.current_id += 1
            self.proto.join_response(conn, not self.playing, self.current_id)
            if not self.playing:
                self.users[conn] = (self.current_id, data["nickname"], data["public_key"])
                self.users_by_seq[self.current_id] = conn
                print("Player joined playing area")
            else:
                print("Join request denied")
                self.close_conn(conn)
        elif data["client"] == "caller":
            self.proto.join_response(conn, self.caller is None, 0)
            if self.caller is None:
                self.users[conn] = (0, data["nickname"], data["public_key"])
                self.users_by_seq[0] = conn
                self.caller = conn
                print("Caller joined playing area")
            else:
                print("Join request denied, caller already exists")
                self.close_conn(conn)
        else:
            self.proto.join_response(conn, False)
            print("Join request denied, unknown client")
            self.close_conn(conn)



    def handle_ready(self, conn, data, signature):
        print("Ready received")
        self.playing = True
        self.proto.ready_response(conn, [tup for tup in self.users.values()])
        print("Ready response sent")



    def handle_start(self, conn, data, signature):
        print("Start received")
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
        print("Start sent to other players")



    def handle_card(self, conn, data, signature):
        print("Card received from", data["seq"])
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
        print("Card sent to other players")



    def handle_deck(self, conn, data, signature):
        print("Deck received from", data["seq"])
        if self.total_shuffles != 0:
            self.proto.redirect(self.caller, data, signature)
            print("Deck sent to caller")
        if self.total_shuffles < len(self.users) - 1:
            self.proto.redirect(self.users_by_seq[self.total_shuffles + 1], data, signature)
            self.total_shuffles += 1
            print("Deck sent to next player")

    

    def handle_final_deck(self, conn, data, signature):
        print("Final deck received from", data["seq"])
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
        print("Final deck sent to other players")



    def handle_key(self, conn, data, signature):
        print("Key received from", data["seq"])
        self.all_keys[data["seq"]] = data["key"]
        if len(self.all_keys) == len(self.users):
            keys_lst = [self.all_keys[i] for i in range(self.current_id+1) if i in self.all_keys]
            keys_lst.reverse()
            for c in self.users:
                self.proto.keys_response(c, keys_lst)
            print("Keys sent to all players")


    
    def handle_winners(self, conn, data, signature):
        print("Winners received from", data["seq"])
        self.proto.redirect(self.caller, data, signature)
        print("Winners sent to caller")


    
    def handle_final_winners(self, conn, data, signature):
        print("Final winners received from", data["seq"])
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
        print("Final winners sent to other players")
        self.playing = False
        self.current_id = 0
        self.total_shuffles = 0
        self.all_keys = {}
        self.all_msgs = []



    def accept(self, sock, mask):
        conn, addr = sock.accept()
        print("Trying to join playing area: ", addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)



    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            # try:
                # TODO verificar seq com conn
                # TODO verificar assinatura
                # print("Received message: ", data)
                self.handlers[data["data"]["type"]](conn, data["data"], data["signature"])
            # except Exception as e:
            #     print("Invalid message received")
            #     print("Error:", e)
            #     exit(1)
        else:
            self.close_conn(conn)

    

    def close_conn(self, conn: socket.socket):
        if conn in self.users:
            print("Connection closed user: ", conn.getpeername())
            del self.users_by_seq[self.users[conn][0]]
            del self.users[conn]

        self.sel.unregister(conn)
        conn.close()



    def other_conns(self, conn: socket.socket):
        for c in self.users:
            if c != conn:
                yield c



    def run(self):
        """ Run until canceled """
        while True:
            events = self.sel.select(0) 
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)