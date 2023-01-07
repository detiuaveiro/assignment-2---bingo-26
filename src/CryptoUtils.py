import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

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

    def encrypt_list(_list, key, iv, mode, to_bytes=True):
        if to_bytes:
            return [Scrypt.encrypt(item.to_bytes(16, 'big'), key, iv, mode) for item in _list]
        return [Scrypt.encrypt(item, key, iv, mode) for item in _list]

    def decrypt(ct, key, iv, mode):
        cipher = Cipher(algorithms.AES(key), Scrypt.algorithm_mode(mode, iv))
        decryptor = cipher.decryptor()
        content = decryptor.update(ct) + decryptor.finalize()
        # unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        # content = unpadder.update(content) + unpadder.finalize()
        return content

    def decrypt_list(_list, key, iv, mode, to_int=True):
        if to_int:
            return [int.from_bytes(Scrypt.decrypt(item, key, iv, mode), 'big') for item in _list]
        return [Scrypt.decrypt(item, key, iv, mode) for item in _list]


class Ascrypt:
    def generate_key_pair(size=2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
        )
        return private_key, private_key.public_key()

    def bytes_from(public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
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
        except:
            return False
        return True

    def serialize_key(public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        