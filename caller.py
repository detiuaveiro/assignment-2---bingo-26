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
args.add_argument('port', type=int, help='Port to listen on', metavar='PORT')
args.add_argument('-area', '-a', type=int, default=5000, help='Player Area port', metavar='PLAYER_AREA_PORT')
PORT = args.parse_args().port
PLAYER_AREA_PORT = args.parse_args().area

recv_sock = socket.socket()
recv_sock.bind(('localhost', PORT))
recv_sock.listen(100)
recv_sock.setblocking(False)
sel.register(recv_sock, selectors.EVENT_READ, accept)

sock = socket.socket()
sock.connect(('localhost', PLAYER_AREA_PORT))
sock.sendall(b'hello')

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)