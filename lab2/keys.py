from enums import *

from base64 import b64encode, b64decode
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class SymmetricKey:
    def __init__(self, key_type: str = "AES", key_length: int = 16, mode: str = "OFB"):
        if key_type not in SYMMETRIC_TYPES.keys():
            raise ValueError
        if mode not in (AES_MODES.keys()):
            raise ValueError
        self.type = SYMMETRIC_TYPES[key_type]
        self.length = key_length
        self.block_size = self.type.block_size
        self.iv = get_random_bytes(self.block_size)

        if key_type == "AES":
            self.mode = AES_MODES[mode]
            self.key = get_random_bytes(self.length)
        else:
            self.mode = DES3_MODES[mode]
            self.key = DES3.adjust_key_parity(get_random_bytes(self.length * 3))

        args = {}
        if mode in ("ECB", "CTR"):
            args["iv"] = self.iv
        if mode == "CTR":
            args["nonce"] = b""

        self.system = self.type.new(key=self.key, mode=self.mode, **args)
        self.arguments = dict()

    def encode(self, text: str):
        plain_text = pad(text.encode("utf8"), self.block_size)
        cipher_text = self.system.encrypt(plain_text)

        return b64encode(cipher_text)

    def decode(self, coded_text: bytes):
        decoded_text = b64decode(coded_text)
        plain_text = self.system.decrpyt(decoded_text)
        return unpad(plain_text, self.block_size)

    def save(self, path):
        return

    def load(self, path):
        return


class AsymmetricKey:
    def __init__(self):
        self.b = 1

    def encode(self, text: str):
        return

    def decode(self, coded_text: bytes):
        return

    def save(self, path):
        return

    def load(self, path):
        return
