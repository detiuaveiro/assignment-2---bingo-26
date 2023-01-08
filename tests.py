from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Scrypt, Ascrypt

# sym_key = Scrypt.generate_symmetric_key()
# iv = Scrypt.generate_iv()
# deck = [1, 2, 3, 4]
# deck_enc = Scrypt.encrypt_list(deck, sym_key, iv, "CBC")
# print(Scrypt.decrypt_list(deck_enc, sym_key, iv, "CBC"))

import pickle
import random
# priv_key, pub_key = Ascrypt.generate_key_pair()
# content = pickle.dumps({"data": 1})
# signature = Ascrypt.sign(priv_key, content)
# print(Ascrypt.verify(pub_key, content, signature))


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

def my_decorator(user_type):
    def decorator(function):
        def wrapper(*args, **kwargs):
            print(user_type)
            result = function(*args, **kwargs)
            result += 1
            return result
        return wrapper
    return decorator

@my_decorator(user_type = "admin")
def test(x):
    return x

print(test(1))