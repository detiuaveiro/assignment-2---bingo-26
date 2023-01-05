import socket
import selectors
from src.BingoProtocol import BingoProtocol


class User:
    def __init__(self, nickname, parea_host, parea_port):
        self.nickname = nickname
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

        # self.cc_key_pair ...


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
            self.SN = data["SN"] # sequence number
        else:
            print("Join request denied")
            self.sel.unregister(self.sock)
            self.sock.close()
            exit(0)


    def run(self):
        while True:
            events = self.sel.select(0)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)