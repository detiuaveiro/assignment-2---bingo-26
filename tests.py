from src.BingoProtocol import BingoProtocol
from src.CryptoUtils import Scrypt, Ascrypt

# sym_key = Scrypt.generate_symmetric_key()
# iv = Scrypt.generate_iv()
# deck = [1, 2, 3, 4]
# deck_enc = Scrypt.encrypt_list(deck, sym_key, iv, "CBC")
# print(Scrypt.decrypt_list(deck_enc, sym_key, iv, "CBC"))

import pickle
priv_key, pub_key = Ascrypt.generate_key_pair()
content = pickle.dumps({"data": 1})
signature = Ascrypt.sign(priv_key, content)
print(Ascrypt.verify(pub_key, content, signature))


# proto = BingoProtocol()
# print(proto.join(None, '...', 'test', b'', b''))

# def get_winner(cards, deck):
#     win_pos = []
#     for card, seq in cards:
#         for idx in range(3, len(deck)+1):
#             card_set = set(card)
#             deck_set = set(deck[:idx])
#             print(card_set, deck_set)
#             if card_set.issubset(deck_set):
#                 win_pos.append((seq, idx))
#                 break
#     win_pos.sort(key=lambda x: x[1])
#     print(win_pos)
#     winners = []
#     for winner in win_pos:
#         if winner[1] == win_pos[0][1]:
#             winners.append(winner[0])
#         else:
#             break
#     print(winners)

# cards = [
#     ([1,2,5],1),
#     ([4,5,1],2),
#     ([7,8,9],3)
# ]
# deck = [1,2,3,4,5,6,7,8,9]
# get_winner(cards, deck)