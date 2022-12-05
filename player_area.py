import selectors
import socket
import argparse
from protocol import *
from crypto import *

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = BingoProtocol.recv_msg(conn)
    print('received: "%s"', str(data))
    if data:
        if isinstance(data, JoinMessage):
            pass
    else:
        sel.unregister(conn)
        conn.close()

args = argparse.ArgumentParser()
args.add_argument('-p', '--port', type=int, default=5000, help='Port to listen on', metavar='PORT')
PORT = args.parse_args().port

sock = socket.socket()
sock.bind(('localhost', PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)