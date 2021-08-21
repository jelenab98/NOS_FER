from base64 import b64encode, b64decode


def save_rsa_keys(private_key, public_key, path, sender=True):
    """
    Helper method for saving RSA keys.
    :param private_key: private RSA key
    :param public_key: public RSA key
    :param path: path to the folder where the keys will be stored
    :param sender: flag if the keys are from the sender or from receiver.
    :return:
    """
    if sender:
        person = "sender"
    else:
        person = "receiver"
    with (path / f"private_{person}_key.pem").open(mode="wb") as f:
        f.write(private_key)

    with (path / f"public_{person}_key.pem").open(mode="wb") as f:
        f.write(public_key)


def load_rsa_keys(path, sender=True):
    """
    Loades RSA keys.
    :param path: path to the folder with the RSA keys
    :param sender: flag if the keys are from the sender or from receiver.
    :return:
    """
    if sender:
        person = "sender"
    else:
        person = "receiver"
    with (path / f"private_{person}_key.pem").open(mode="rb") as f:
        private_key = f.read()

    with (path / f"public_{person}_key.pem").open(mode="rb") as f:
        public_key = f.read()

    return private_key, public_key


def save_component(path, component):
    """
    Helper method for saving b64 encoded components (signature, envelope, iv,...).
    :param path: path to the file in which the file will be saved.
    :param component: component to be saved.
    :return:
    """
    with path.open(mode="wb") as f:
        f.write(b64encode(component))


def load_component(path):
    """
    Helper ethod for loading the b64 encoded component.
    :param path: path to the file to be read.
    :return:
    """
    with path.open(mode="rb") as f:
        component = f.read()
    return b64decode(component)
