import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.shared.utils.db import SqlRunner
from app.shared.config.env import env_settings

from . import repository as credentials_repo
from .dto import PublicKeyResponse


def load_server_private_key(*, db: SqlRunner) -> Ed25519PrivateKey:
    """
    Load and decrypt the server's private key from the database.

    Format: [salt(16B) | iv(12B) | ciphertext(N) | tag(16B)]
    """
    data = credentials_repo.get_server_private_key_encrypted(db=db)

    if len(data) < 16 + 12 + 16:
        raise ValueError("Corrupted key file: too short")

    salt = data[:16]
    iv = data[16:28]
    tag = data[-16:]
    ciphertext = data[28:-16]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=65536,
        backend=default_backend(),
    )
    key = kdf.derive(env_settings.server_private_key_password.encode("utf-8"))

    decryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
    ).decryptor()

    private_key_bytes = decryptor.update(ciphertext) + decryptor.finalize()

    return Ed25519PrivateKey.from_private_bytes(private_key_bytes)


def get_public_key(*, db: SqlRunner) -> PublicKeyResponse:
    """Get the server's public key for encrypting data."""
    private_key = load_server_private_key(db=db)
    print("FIZZ: were good", private_key)
    public_key_bytes = private_key.public_key().public_bytes_raw()
    return PublicKeyResponse(
        public_key=base64.b64encode(public_key_bytes).decode("utf-8")
    )
