from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sympadding
from cryptography.hazmat.backends import default_backend
import os

backend = default_backend()

# Simple OR policy ABE implementation
class AttributeAuthority:
    def generate_attribute(self, name: str):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=backend)
        private_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return name, private_bytes, public_bytes


def encrypt(data: bytes, attribute_public_keys: list):
    # Generate symmetric key
    sym_key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(sym_key), modes.CBC(iv), backend=backend)
    padder = sympadding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    ciphertext = iv + ciphertext

    wrapped_keys = []
    for pub_bytes in attribute_public_keys:
        pub_key = serialization.load_pem_public_key(pub_bytes, backend=backend)
        wrapped = pub_key.encrypt(
            sym_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        wrapped_keys.append(wrapped)
    return ciphertext, wrapped_keys


def decrypt(ciphertext: bytes, wrapped_key: bytes, private_key_bytes: bytes):
    priv_key = serialization.load_pem_private_key(private_key_bytes, password=None, backend=backend)
    sym_key = priv_key.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    iv = ciphertext[:16]
    ct = ciphertext[16:]
    cipher = Cipher(algorithms.AES(sym_key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    unpadder = sympadding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded) + unpadder.finalize()
    return data
