import PyKCS11
import json
from cryptography import x509
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash

class CitizenCard:
    def __init__(self, pin, lib='/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'):
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(lib)
        slot = pkcs11.getSlotList(tokenPresent=True)[0]
        assert "Auth" in pkcs11.getTokenInfo(slot).label
        self.session = pkcs11.openSession(slot)
        self.session.login(pin)
        self.private_key = self.session.findObjects([
                            (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                            (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY")
                            ])[0]


    def export_cert(self):
        cert_obj = self.session.findObjects([
                            (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                            (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
                            ])[0]
        cert_der_data = cert_obj.to_dict()['CKA_VALUE']
        return json.dumps(cert_der_data)
    

    def sign(self, obj):
        signature = bytes(self.session.sign(self.private_key, obj, PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)))
        #print("signature: ", binascii.hexlify(signature))
        return signature


    # static method (not associated with any instance)
    def get_pub_key_from_cert(obj):
        cert_der_data = bytes(json.loads(obj))
        cert = x509.load_der_x509_certificate(cert_der_data, db())
        return cert.public_key()


    # static method (not associated with any instance)
    def check_nationality(obj, country):
        cert_der_data = bytes(json.loads(obj))
        cert = x509.load_der_x509_certificate(cert_der_data, db())
        for attr in cert.subject.rfc4514_string().split(","):
            if attr.startswith("C="):
                c = attr.split("=")[1]
                return c == country
        return False


    # static method (not associated with any instance)
    def verify(public_key, obj, signature):
        try:
            md = Hash(SHA1(), backend=db())
            md.update(obj)
            digest = md.finalize()
            public_key.verify(
                signature,
                digest,
                PKCS1v15(),
                SHA1()
            )
            return True
        except:
            pass

        try:
            public_key.verify(
                signature,
                obj,
                PKCS1v15(),
                SHA1()
            )
            return True
        except:
            return False