from enums import *


class Hash:
    def __init__(self, family: int = 2, key: int = 256):
        if family not in (2, 3):
            raise ValueError
        if key not in (224, 256, 384, 512):
            raise ValueError

        if family == 2:
            self.hash = SHA2_TYPES[key].new()
        else:
            self.hash = SHA3_TYPES[key].new()

    def update(self, text: str):
        self.hash.update(text.encode("utf8"))

    def get_hash(self, text: str):
        self.update(text)
        return self.hash.digest()

    def save(self, path):
        return

    def load(self, path):
        return


if __name__ == '__main__':
    h = Hash(2, 256)
    H = h.get_hash("Danas.")
    print(H)