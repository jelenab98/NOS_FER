from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA


def get_public_private_keys(key_length, crypto_algorithm):
    """
    Creates public and private RSA keys.
    :param key_length: length of the keys
    :param crypto_algorithm: algorithm (RSA)
    :return:
    """
    key = crypto_algorithm.generate(key_length)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key


def get_signature(message, hash_mode, key):
    """
    Creates digital signature of a message
    :param message: message to sign
    :param hash_mode: type of hash method to use
    :param key: private key to sign
    :return:
    """
    if type(message) == str:
        message = message.encode("utf-8")
    hashed_message = hash_mode.new(message)
    return pkcs1_15.new(key).sign(hashed_message)


def verify_signature(message, signature, hash_mode, key):
    """
    Verifies the signature
    :param message: message to verify
    :param signature: signature to verify
    :param hash_mode: type of hash mode to use
    :param key: public key to use for verification
    :return:
    """
    if type(message) == str:
        message = message.encode("utf-8")
    hashed_message = hash_mode.new(message)
    try:
        pkcs1_15.new(key).verify(hashed_message, signature)
        print("Signature is valid!")
    except (ValueError, TypeError):
        print("Signature is not valid!")


def get_envelope(message, crypto_algorithm, crypto_mode, key_length, key, padding, iv_length):
    """
    Creates digital envelope.
    :param message: message to send
    :param crypto_algorithm: symmetric crypto algorithm to encrypt the message
    :param crypto_mode: symmetric crypto mode
    :param key_length: length of symmetric key
    :param key: RSA key
    :param padding: padding for the message
    :param iv_length: length of the random IV vector
    :return:
    """
    _key = get_random_bytes(int(key_length/8))

    iv = get_random_bytes(iv_length)
    cipher = crypto_algorithm.new(_key, crypto_mode, iv)

    cypher_text = cipher.encrypt(pad(message.encode("utf-8"), padding))
    cypher_key = PKCS1_OAEP.new(key).encrypt(_key)

    return cypher_text, cypher_key, iv


def decrypt_envelope(cypher_text, cypher_key, crypto_algorithm, crypto_mode, key, padding, iv):
    """
    Decrypts the envelope and returns the message.
    :param cypher_text: encrypted message from the envelope
    :param cypher_key: encrypted key from the envelope
    :param crypto_algorithm: symmetric algorithm used for encryption
    :param crypto_mode: symmetric crypto mode
    :param key: RSA key
    :param padding: padding for the text
    :param iv: random initial vector
    :return:
    """
    rsa = PKCS1_OAEP.new(key)
    _key = rsa.decrypt(cypher_key)

    cipher = crypto_algorithm.new(_key, crypto_mode, iv)

    message = unpad(cipher.decrypt(cypher_text), padding)

    return message.decode("utf-8")


def get_stamp(message, crypto_algorithm, crypto_mode, key_length, public_key,
              private_key, hash_mode, padding, iv_length):
    """
    Creates digital stamp - signed digital envelope.
    :param message: message to be sent
    :param crypto_algorithm: symmetric crypto algorithm
    :param crypto_mode: mode of the crypto algorithm
    :param key_length: length of the symmetric key
    :param public_key: RSa key
    :param padding: padding of the text
    :param iv_length: length of the random initial vector
    :param private_key: RSA key
    :param hash_mode: type of hash algorithm
    :return:
    """

    cypher_text, cypher_key, iv = get_envelope(message, crypto_algorithm, crypto_mode,
                                               key_length, public_key, padding, iv_length)

    signature = get_signature(cypher_text + cypher_key, hash_mode, private_key)

    return cypher_text, cypher_key, iv, signature


def verify_stamp(cypher_text, cypher_key, public_key, hash_mode, signature):
    """
    Verification of stamp
    :param cypher_text: encrypted message from the envelope
    :param cypher_key: encrypted key from the envelope
    :param public_key: RSA key
    :param hash_mode: type of hash algorithm
    :param signature: signature to verify
    :return:
    """
    verify_signature(cypher_text + cypher_key, signature, hash_mode, public_key)
