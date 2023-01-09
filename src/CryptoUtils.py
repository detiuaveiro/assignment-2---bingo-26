import os
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class BytesSerializer:
    def to_base64_str(obj: bytes) -> str:
        return base64.b64encode(obj).decode("utf-8")

    def from_base64_str(string: str) -> bytes:
        return base64.b64decode(string.encode("utf-8"))


class Scrypt:
    def algorithm_mode(mode, iv):
        if mode == "cbc":
            return modes.CBC(iv)
        elif mode == "ofb":
            return modes.OFB(iv)
        elif mode == "cfb":
            return modes.CFB(iv)
        else:
            return modes.ECB()

    generate_symmetric_key = lambda: os.urandom(32)
    generate_iv = lambda: os.urandom(16)

    def encrypt(content, key, iv, mode):
        # padder = PKCS7(algorithms.AES.block_size).padder()
        # content = padder.update(content) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), Scrypt.algorithm_mode(mode, iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(content) + encryptor.finalize()
        return ct

    def encrypt_list(_list, key, iv, mode, serializable=True):
        res = []
        for item in _list:
            if type(item) == str: item = base64.b64decode(item.encode("utf-8"))
            elif type(item) == int: item = item.to_bytes(16, 'big')
            if serializable: res.append(BytesSerializer.to_base64_str(Scrypt.encrypt(item, key, iv, mode)))
            else: res.append(Scrypt.encrypt(item, key, iv, mode))
        return res


    def decrypt(ct, key, iv, mode):
        cipher = Cipher(algorithms.AES(key), Scrypt.algorithm_mode(mode, iv))
        decryptor = cipher.decryptor()
        content = decryptor.update(ct) + decryptor.finalize()
        # unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        # content = unpadder.update(content) + unpadder.finalize()
        return content

    def decrypt_list(_list, key, iv, mode, to_int = True):
        res = []
        for item in _list:
            if type(item) == str: item = BytesSerializer.from_base64_str(item)
            if to_int: res.append(int.from_bytes(Scrypt.decrypt(item, key, iv, mode), 'big'))
            else: res.append(Scrypt.decrypt(item, key, iv, mode))
        return res


class Ascrypt:
    def generate_key_pair(size=2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
        )
        return private_key, private_key.public_key()

    def serialize_key(public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")

    def deserialize_key(key: str):
        return serialization.load_pem_public_key(key.encode("utf-8"))
    
    def sign(private_key, content):
        return private_key.sign(
            content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(public_key, content, signature):
        try:
            public_key.verify(
                signature,
                content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def msg_hash(self, msg):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(msg)
        return digest.finalize()