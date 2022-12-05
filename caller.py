from protocol import *
from crypto import *
import selectors
import socket
import argparse

sel = selectors.DefaultSelector()

def read(conn, mask):
    data = BingoProtocol.rcv(conn)
    if data:
        if data["type"] == "ack":
            print("ACK:", data["command"])
    else:
        sel.unregister(conn)
        conn.close()

args = argparse.ArgumentParser()
args.add_argument('--addr', type=str, help='Player Area IP address', metavar='ADDR', default='localhost')
args.add_argument('-p', '--port', type=int, default=5000, help='Player Area port', metavar='PLAYER_AREA_PORT')
parsed_args = args.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect((parsed_args.addr, parsed_args.port))
sel.register(sock, selectors.EVENT_READ, read)
sock.sendall(b'hello')

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)