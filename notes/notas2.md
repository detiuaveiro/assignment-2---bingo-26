Project 2 - Secure Game

Bingo: the game

Bingo is a game that can take a variable number of players. We will not deal with the monetary dimension of it. Each player receives a card with a random set of M unique numbers (from 1 to , but not all, since M < N) and those numbers (deck) are then randomly selected by a caller (the game host, the entity that coordinates the evolution of the game) until a player completes a row in their card with the numbers selected so far. That player is the winner. It is possible to have several winners, though.


BINGO CARD:

|B   I   N   G   O |

|8   16  45  55  74|

|1   25  31  51  62|

|12  29  FR  49  65|

|5   21  42  53  71|

|6   18  36  47  68|



BINGO EXPLAINED:
https://www.youtube.com/watch?v=nGCEpUAnkSg

SOCKET TUTORIAL:
https://realpython.com/python-sockets/
 
SMARTCARD GUIDE:
https://pyscard.sourceforge.io/user-guide.html#pyscard-user-guide


# get citizen card
cert_obj = session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                    (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
                    ])[0]
cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])
public_key = x509.load_der_x509_certificate(cert_der_data, db()).public_key()

private_key = session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                    (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION KEY')
                    ])[0]

data = b'Hello World'
signature = session.sign(private_key, data, PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None))
print("Signature: ", signature)
print("Signature: ", binascii.hexlify(signature))
exit()

# hash
h = Hash(SHA1())
h.update(data)
digest = h.finalize()
print("Hash: ", digest)
print("Hash: ", binascii.hexlify(digest))

# verify hash
assert public_key.verify(
    signature,
    digest,
    PKCS1v15(),
    SHA1()
)