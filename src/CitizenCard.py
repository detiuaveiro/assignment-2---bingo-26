from getpass import getpass
import PyKCS11
import binascii
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash

lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'

pkcs11 = PyKCS11.PyKCS11Lib()
pkcs11.load(lib)
slot = pkcs11.getSlotList(tokenPresent=True)[0]

assert "Auth" in pkcs11.getTokenInfo(slot).label

session = pkcs11.openSession(slot)
session.login("9792")

private_key = session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                    (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY")
                    ])[0]

cert_obj = session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                    (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
                    ])[0]
cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])
cert = x509.load_der_x509_certificate(cert_der_data, db())
public_key = cert.public_key()

text = b'text to sign'
signature = bytes(session.sign(private_key, text, PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)))
print("signature: ", binascii.hexlify(signature))


md = Hash(SHA1(), backend=db())
md.update(text)
digest = md.finalize()


public_key = cert.public_key()

public_key.verify(
    signature,
    digest,
    PKCS1v15(),
    SHA1()
)