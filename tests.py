from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Scrypt, Ascrypt
from src.CitizenCard import CitizenCard

import logging
logging.basicConfig(
    filename='playing_area.log',
    encoding='utf-8',
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


class color:
    WARNING = ('\033[93m', logging.WARNING)
    FAIL = ('\033[91m', logging.ERROR) 
    ENDC = ('\033[92m', logging.INFO)

def log(msg, level="INFO"):
    if level == "ERROR":
        logging.log(logging.ERROR, msg)
        print(color.FAIL[0] + f"ERROR: {msg}" + color.ENDC[0])
    elif level == "WARNING":
        logging.warning(msg)
        print(color.WARNING[0] + f"WARNING: {msg}" + color.ENDC[0])
    else:
        logging.info(msg)
        print(color.ENDC[0] + f"INFO: {msg}" + color.ENDC[0])

log("ola mundo", "ERROR")
log("ola mundo", "WARNING")
log("ola mundo", "INFO")


# ------------------------------------------------------------------

# cc = CitizenCard("1111")
# msg = b'ola mundo'
# signature = cc.sign(msg)
# print(CitizenCard.verify(cc.export_cert_public_key(), msg, signature))

# ------------------------------------------------------------------

# import logging
# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG, format='%(levelname)s: %(message)s')
# logging.info('So should this')
# logging.warning('And this, too')

# ------------------------------------------------------------------
# sym_key = Scrypt.generate_symmetric_key()
# iv = Scrypt.generate_iv()
# deck = [1, 2, 3, 4]
# deck_enc = Scrypt.encrypt_list(deck, sym_key, iv, "CBC")
# print(Scrypt.decrypt_list(deck_enc, sym_key, iv, "CBC"))

# ------------------------------------------------------------------

#import pickle
#import random
# priv_key, pub_key = Ascrypt.generate_key_pair()
# content = pickle.dumps({"data": 1})
# signature = Ascrypt.sign(priv_key, content)
# print(Ascrypt.verify(pub_key, content, signature))

# ------------------------------------------------------------------

# proto = BingoProtocol()
# print(proto.join(None, '...', 'test', b'', b''))

# def get_winner(cards, deck):
#     print(cards)
#     win_pos = []
#     for card, seq in cards:
#         counter = 0
#         for idx, num in enumerate(deck):
#             if num in card:
#                 counter += 1
#             if counter == 3:
#                 win_pos.append((seq, idx))
#                 break
#     win_pos.sort(key=lambda x: (x[1], x[0]))
#     print(win_pos)
#     winners = []
#     for winner in win_pos:
#         if winner[1] == win_pos[0][1]:
#             winners.append(winner[0])
#         else:
#             break
#     print(winners)


# cards = [
#     (random.sample(range(1, 10), 3), 1),
#     (random.sample(range(1, 10), 3), 2),
#     (random.sample(range(1, 10), 3), 3),
# ]
# deck = [1,2,3,4,5,6,7,8,9]
# get_winner(cards, deck)

# ------------------------------------------------------------------

# def decorator(func):
#     def wrapper(*args, **kwargs):
#         print(kwargs['user_type'])
#         res = func(*args, **kwargs)
#         return res
#     return wrapper

# @decorator(user_type = "admin")
# def test(x):
#     return x

# print(test(1))

# def my_decorator(user_type):
#     def decorator(function):
#         def wrapper(*args, **kwargs):
#             print(user_type)
#             result = function(*args, **kwargs)
#             result += 1
#             return result
#         return wrapper
#     return decorator

# @my_decorator(user_type = "admin")
# def test(x):
#     return x

# print(test(1))

# ------------------------------------------------------------------

# class aaa:
#     def __init__(self, x):
#         self.x = x

# a1= aaa(1)
# a1.x = 2
# print(a1.x)
# a1.__init__(3)
# print(a1.x)

# ------------------------------------------------------------------

# from src.CryptoUtils import Scrypt, Ascrypt, BytesSerializer


# import json
# sym_key = Scrypt.generate_symmetric_key()
# iv = Scrypt.generate_iv()
# obj_recv = json.dumps({"sym_key": BytesSerializer.to_base64_str(sym_key), "iv": BytesSerializer.to_base64_str(iv)}).encode("utf-8")
# obj = obj_recv.decode("utf-8")
# obj = json.loads(obj)
# sym_key_recv = BytesSerializer.from_base64_str(obj["sym_key"])
# iv_recv = BytesSerializer.from_base64_str(obj["iv"])
# print(sym_key == sym_key_recv)
# print(iv == iv_recv)