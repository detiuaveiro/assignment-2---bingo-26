from protocol import *
from crypto import *
import selectors
import socket
import argparse

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    print('ACCEPTED:', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = BingoProtocol.rcv(conn)
    if data:
        if data["type"] == "join":
            print("JOIN:", data["host"])
            BingoProtocol.ack(conn, "join")
    else:
        sel.unregister(conn)
        conn.close()

args = argparse.ArgumentParser()
args.add_argument('-p', '--port', type=int, default=5000, help='Port to listen on', metavar='PORT')
PORT = args.parse_args().port

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
sock.bind(('localhost', PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)