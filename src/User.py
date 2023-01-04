import socket
import selectors
from src.BingoProtocol import BingoProtocol


class User:
    def __init__(self, parea_host, parea_port):
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


    def read(self, conn, mask):
        data = self.proto.rcv(conn)
        if data:
            print("Received:", data)
            if data["type"] in self.handlers:
                self.handlers[data["type"]](conn, data["data"])
            else:
                print("Unknown type:", data["type"])
        else:
            print("Connection closed by playing area:", conn.getpeername())
            self.sel.unregister(conn)
            conn.close()
            exit(0)


    def join_response(self, conn: socket.socket, data: dict):
        if data["accepted"]:
            print("Joined playing area")
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