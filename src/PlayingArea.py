import socket
import selectors
import json
import time
import logging
from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Ascrypt, BytesSerializer, Hashing
from src.CitizenCard import CitizenCard


class BingoException(Exception):
    pass

class color:
    WARNING = ('\033[93m', logging.WARNING)
    FAIL = ('\033[91m', logging.ERROR) 
    ENDC = ('\033[0m', logging.INFO)

logging.basicConfig(filename='playing_area.log', encoding='utf-8', level=logging.DEBUG, format='%(levelname)s: %(message)s')

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

        self.users_by_seq = {}        # {seq: conn}
        self.users = {}               # {conn: (seq, nickname, public_key)}
        self.caller = None
        self.current_id = 0
        self.total_shuffles = 0
        self.all_keys = {}
        self.playing = False          # blocks new players from joining
        self.logs = []

        # asymmetric encryption
        self.private_key, self.public_key = Ascrypt.generate_key_pair()
        self.proto = BingoProtocol(self.private_key)

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
        print(f"Player {data['target_seq']} disqualified for : ", data["reason"])
        self.log_event(f"Player {data['target_seq']} disqualified for : ", data["seq"], signature)
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.log_event(f"Disqualification message sent to player {self.users[c][0]}", None, s)
        print("Disqualification message sent to other players")
        self.close_conn(self.users_by_seq[data["target_seq"]])
        self.reset()



    def handle_get_logs(self, conn, data, signature):
        print("Logs requested")
        self.proto.logs_response(conn, self.logs)
        print("Logs sent")



    def handle_join(self, conn, data, signature):
        if data["client"] == "player":
            self.current_id += 1
            self.proto.join_response(conn, not self.playing, self.current_id, Ascrypt.serialize_key(self.public_key))
            s = self.proto.join_response(None, not self.playing, self.current_id, Ascrypt.serialize_key(self.public_key))["signature"]
            self.log_event("Join response sent", None, s)
            if not self.playing:
                self.users[conn] = (self.current_id, data["nickname"], data["public_key"])
                self.users_by_seq[self.current_id] = conn
                print("Player joined playing area")
                self.log_event("Player joined playing area", self.current_id, signature)
            else:
                print("Join request denied")
                self.log_event("Join request denied", None, signature)
                self.close_conn(conn)
        elif data["client"] == "caller":
            self.proto.join_response(conn, self.caller is None, 0, Ascrypt.serialize_key(self.public_key))
            s = self.proto.join_response(None, self.caller is None, 0, Ascrypt.serialize_key(self.public_key))["signature"]
            self.log_event("Join response sent", None, s)

            if self.caller is None:
                self.users[conn] = (0, data["nickname"], data["public_key"])
                self.users_by_seq[0] = conn
                self.caller = conn
                print("Caller joined playing area")
                self.log_event("Caller joined playing area", 0, signature)
            else:
                print("Join request denied, caller already exists")
                self.log_event("Join request denied, caller already exists", None, signature)
                self.close_conn(conn)
        else:
            print("Join request denied, unknown client")
            self.close_conn(conn)



    def handle_ready(self, conn, data, signature):
        self.logs = []
        print("Ready received")
        self.log_event("Ready received", data["seq"], signature)
        self.playing = True
        players = [tup for tup in self.users.values()]
        self.proto.ready_response(conn, players)
        print("Ready response sent")
        s = self.proto.ready_response(None, players)["signature"]
        self.log_event("Ready response sent", None, s)
        if len(players) <= 1:
            self.reset()



    def handle_start(self, conn, data, signature):
        print("Start received")
        self.log_event("Start received", data["seq"], signature)
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.log_event(f"Start sent to player {self.users[c][0]}", None, s)
        print("Start sent to other players")



    def handle_card(self, conn, data, signature):
        print("Card received from", data["seq"])
        self.log_event("Card received", data["seq"], signature)
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.log_event(f"Card sent to player {self.users[c][0]}", None, s)

        print("Card sent to other players")



    def handle_deck(self, conn, data, signature):
        print("Deck received from", data["seq"])
        self.log_event("Deck received", data["seq"], signature)
        if self.total_shuffles != 0:
            self.proto.redirect(self.caller, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            print("Deck sent to caller")
            self.log_event("Deck sent to caller", None, s)
        if self.total_shuffles < len(self.users) - 1:
            self.proto.redirect(self.users_by_seq[self.total_shuffles + 1], data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.total_shuffles += 1
            print("Deck sent to next player")
            self.log_event("Deck sent to next player", None, s)

    

    def handle_final_deck(self, conn, data, signature):
        print("Final deck received from", data["seq"])
        self.log_event("Final deck received from", data["seq"], signature)
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.log_event(f"Final deck sent to player {self.users[c][0]}", None, s)
        print("Final deck sent to other players")



    def handle_key(self, conn, data, signature):
        print("Key received from", data["seq"])
        self.log_event("Key received", data["seq"], signature)
        self.all_keys[data["seq"]] = data["key"]
        if len(self.all_keys) == len(self.users):
            keys_lst = [self.all_keys[i] for i in range(self.current_id+1) if i in self.all_keys]
            keys_lst.reverse()
            for c in self.users:
                self.proto.keys_response(c, keys_lst)
                s = self.proto.keys_response(None, keys_lst)["signature"]
                self.log_event(f"Keys sent to player {self.users[c][0]}", None, s)
            print("Keys sent to all players")


    
    def handle_winners(self, conn, data, signature):
        print("Winners received from", data["seq"])
        self.log_event("Winner(s) received", data["seq"], signature)
        self.proto.redirect(self.caller, data, signature)
        s = self.proto.redirect(None, data, signature)["signature"]
        print("Winners sent to caller")
        self.log_event("Winners sent to caller", None, s)


    
    def handle_final_winners(self, conn, data, signature):
        print("Final winners received from", data["seq"])
        self.log_event("Final winner(s) received", data["seq"], signature)
        for c in self.other_conns(conn):
            self.proto.redirect(c, data, signature)
            s = self.proto.redirect(None, data, signature)["signature"]
            self.log_event(f"Final winners sent to player {self.users[c][0]}", None, s)
        print("Final winners sent to other players")
        self.reset()
        
        

    def reset(self):
        self.users_by_seq = { k: v for k, v in self.users_by_seq.items() if k == 0 }
        self.users = { k: v for k, v in self.users.items() if v[0] == 0 }
        self.current_id = 0
        self.total_shuffles = 0
        self.all_keys = {}
        self.playing = False



    def accept(self, sock, mask):
        conn, addr = sock.accept()
        print("Trying to join playing area: ", addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)



    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            #try:
                self.verify_seq(conn, data)
                self.verify_type(conn, data)
                self.verify_signature(conn, data)   

                self.handlers[data["data"]["type"]](conn, data["data"], data["signature"])
            #except Exception as e:
            #    print("Invalid message received")
            #    print("Error:", e)
            #    exit(1)
        else:
            self.close_conn(conn)


    
    def verify_seq(self, conn, data) -> bool:
        if data["data"]["type"] in ["join", "get_logs"]:
            return
        seq = data["data"]["seq"]
        if self.users[conn][0] != seq:
            raise BingoException("Wrong sequence number")


        
    def verify_type(self, conn, data) -> bool:
        type_ = data["data"]["type"]
        if type_ not in self.handlers:
            raise BingoException("Unknown message type")
        if type_ in ["join", "get_logs"]:
            return
        available_types = {
            "caller": [
                "disqualify", "ready", "start", "final_deck", "final_winners"
            ],
            "player": [
                "card", "winners"
            ],
            "user": [
                "deck", "key"
            ]
        }
        user_type, = [u for u in available_types if type_ in available_types[u]]
        if user_type == "caller":
            if conn != self.caller:
                raise BingoException("Only caller can send this message")
        elif user_type == "player":
            if conn not in self.other_conns(self.caller):
                raise BingoException("Only players can send this message")
        elif user_type == "user":
            if conn not in self.users:
                raise BingoException("Only users can send this message")



    def verify_signature(self, conn, data) -> bool:
        content = json.dumps(data["data"]).encode("utf-8")
        signature = BytesSerializer.from_base64_str(data["signature"])
        if conn in self.users and not Ascrypt.verify(Ascrypt.deserialize_key(self.users[conn][2]), content, signature):
            print("\033[91mInvalid signature\033[0m")
            raise BingoException("Invalid signature")
        elif data["data"]["type"] == "join":
            if not Ascrypt.verify(Ascrypt.deserialize_key(data["data"]["public_key"]), content, signature):
                print("\033[91mInvalid signature\033[0m")
                raise BingoException("Invalid signature")
            #CARDcc_signature = BytesSerializer.from_base64_str(data["cc_signature"])
            #CARDif not CitizenCard.verify(Ascrypt.deserialize_key(data["data"]["cc_public_key"]), content, cc_signature):
            #CARD   print("\033[91mInvalid Citizen Card signature\033[0m")
            #CARD   raise BingoException("Invalid Citizen Card signature")



    def close_conn(self, conn: socket.socket):
        if conn in self.users:
            print("Connection closed user: ", conn.getpeername())
            del self.users_by_seq[self.users[conn][0]]
            del self.users[conn]
        if conn == self.caller:
            self.caller = None

        self.sel.unregister(conn)
        conn.close()



    def other_conns(self, conn: socket.socket):
        for c in self.users:
            if c != conn:
                yield c



    def log_event(self, msg, seq, signature = "", level = "INFO"):
        if seq is None: seq = "PA"
        hash_= None if len(self.logs) == 0 else Hashing.hash(self.logs[-1])
        msg = f"{seq}, {time.time()}, {msg}, {hash_ }, {signature}"
        # if level == "ERROR":
        #     logging.error(msg)
        #     print(color.FAIL[0] + msg + color.ENDC[0])
        # elif level == "WARNING":
        #     logging.warning(msg)
        #     print(color.WARNING[0] + msg + color.ENDC[0])
        # else:
        #     logging.info(msg)
        #     print(color.ENDC[0] + msg + color.ENDC[0])
        self.logs.append(msg)
        logging.info(msg)



    def run(self):
        """ Run until canceled """
        while True:
            events = self.sel.select(0) 
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)