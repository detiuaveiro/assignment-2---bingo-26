import socket
import selectors
from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Ascrypt
import logging


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
        self.players = {}
        self.caller = {}
        self.playing = False
        # self.public_key, self.private_key = Ascrypt.generate_key_pair()
        # - list of citizens that can act as callers
        # ...
        self.all_msgs = []

        self.handlers = { 
            "join": self.join,
        }


    def accept(self, sock, mask):
        conn, addr = sock.accept()
        print("Trying to join playing area", addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)


    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            print("Received:", data)
            if data["type"] in self.handlers:
                self.handlers[data["type"]](conn, data["data"])
            else:
                print("Unknown type:", data["type"])
        else:
            if conn in self.players:
                print("Connection closed by player: ", conn.getpeername())
                del self.players[conn]
            if conn in self.caller:
                print("Connection closed by caller: ", conn.getpeername())
                del self.caller[conn]
            self.sel.unregister(conn)
            conn.close()

    
    def join(self, conn: socket.socket, data: dict):
        if data["client"] == "player":                
            self.proto.join_response(conn, not self.playing)
            if not self.playing:
                self.players[conn] = conn.getpeername()
                print("Player joined playing area, game in progress")
            else:
                print("Join request denied")
                self.sel.unregister(conn)
                conn.close()
        elif data["client"] == "caller":
            self.proto.join_response(conn, len(self.caller) == 0)
            if len(self.caller) == 0:
                self.caller[conn] = conn.getpeername()
                print("Caller joined playing area")
            else:
                print("Join request denied, caller already exists")
                self.sel.unregister(conn)
                conn.close()
        else:
            self.proto.join_response(conn, False)
            print("Join request denied, unknown client")
            self.sel.unregister(conn)
            conn.close()


    def run(self):
        """ Run until canceled """

        while True:
            events = self.sel.select(0) 
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)