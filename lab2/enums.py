from Cryptodome.Hash import SHA224, SHA256, SHA384, SHA512, SHA3_224, SHA3_256, SHA3_384, SHA3_512
from Cryptodome.Cipher import AES, DES3

SHA2_TYPES = {224: SHA224, 256: SHA256, 384: SHA384, 512: SHA512}
SHA3_TYPES = {224: SHA3_224, 256: SHA3_256, 384: SHA3_384, 512: SHA3_512}

KEY_TYPES = {"AES": AES, "3DES": DES3}

AES_MODES = {"ECB": AES.MODE_ECB, "CBC": AES.MODE_CBC, "CFB": AES.MODE_CFB, "OFB": AES.MODE_OFB, "CTR": AES.MODE_CTR}
DES3_MODES = {"ECB": DES3.MODE_ECB, "CBC": DES3.MODE_CBC, "CFB": DES3.MODE_CFB,
              "OFB": DES3.MODE_OFB, "CTR": DES3.MODE_CTR}
