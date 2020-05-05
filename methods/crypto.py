import binascii, time
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

backend = default_backend()


def password_encrypt(message: bytes, key: bytes) -> bytes:
    current_time = int(time.time()).to_bytes(8, 'big')
    algorithm = algorithms.AES(key)
    iv = secrets.token_bytes(algorithm.block_size // 8)
    cipher = Cipher(algorithm, modes.GCM(iv), backend=backend)
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(current_time)
    ciphertext = encryptor.update(message) + encryptor.finalize()
    return b64e(current_time + iv + ciphertext + encryptor.tag)


def password_decrypt(token: bytes, key: bytes, ttl=None) -> bytes:
    algorithm = algorithms.AES(key)
    try:
        data = b64d(token)
    except (TypeError, binascii.Error):
        raise InvalidToken
    timestamp, iv, tag = data[:8], data[8:algorithm.block_size // 8 + 8], data[-16:]
    if ttl is not None:
        current_time = int(time.time())
        time_encrypted, = int.from_bytes(data[:8], 'big')
        if time_encrypted + ttl < current_time or current_time + 60 < time_encrypted:
            raise InvalidToken
    cipher = Cipher(algorithm, modes.GCM(iv, tag), backend=backend)
    decryptor = cipher.decryptor()
    decryptor.authenticate_additional_data(timestamp)
    ciphertext = data[8 + len(iv):-16]
    return decryptor.update(ciphertext) + decryptor.finalize()
