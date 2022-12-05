import os
import argparse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

class Scrypt:
    def algorithm_mode(self, mode, iv):
        if mode == "cbc":
            return modes.CBC(iv)
        elif mode == "ofb":
            return modes.OFB(iv)
        elif mode == "cfb":
            return modes.CFB(iv)
        else:
            return modes.ECB()

    def encrypt(self, content, mode):
        key = os.urandom(32)
        iv = os.urandom(16)
        padder = PKCS7(algorithms.AES.block_size).padder()
        content = padder.update(content) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), self.algorithm_mode(mode, iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(content) + encryptor.finalize()
        return ct, iv, key

    def decrypt(self, ct, iv, key, mode):
        cipher = Cipher(algorithms.AES(key), self.algorithm_mode(mode, iv))
        decryptor = cipher.decryptor()
        content = decryptor.update(ct) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        content = unpadder.update(content) + unpadder.finalize()
        return content

class Ascrypt:
    def private_key(self, size=2048):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=size,
        )
    
    def public_key(self, private_key):
        return private_key.public_key()

    def bytes_from(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def sign(self, private_key, content):
        return private_key.sign(
            content,
            padding.PSS(    
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self, public_key, content, signature):
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