#!/usr/bin/env python3
"""
Script to generate server-side Ed25519 key pair for secure file transfers.
The private key is encrypted with a password and generates SQL to insert into database.
"""

import sys
import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def encrypt_private_key(private_key_bytes: bytes, password: str) -> bytes:
    """
    Encrypt private_key_bytes with password (PBKDF2 + AES-256-GCM).

    Format: [salt(16B) | iv(12B) | ciphertext(N) | tag(16B)]
    Returns the encrypted data as bytes.
    """
    salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=65536,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode("utf-8"))

    iv = secrets.token_bytes(12)
    encryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv), backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(private_key_bytes) + encryptor.finalize()

    encrypted_data = salt + iv + ciphertext + encryptor.tag

    return encrypted_data


def generate_sql_statement(encrypted_key: bytes) -> str:
    """Generate SQL INSERT statement for storing encrypted private key."""
    sql = f"""INSERT INTO secrets (name, content)
VALUES (
    'server_private_key',
    '\\x{encrypted_key.hex()}'
)
ON CONFLICT (name) DO UPDATE SET content = EXCLUDED.content;"""
    return sql


def main():
    print("=" * 60)
    print("Server Key Pair Generator")
    print("=" * 60)
    print()

    # Get password
    password = input("Enter password to encrypt private key: ").strip()

    if not password:
        print("Error: Password cannot be empty")
        sys.exit(1)

    # Generate Ed25519 key pair
    print()
    print("Generating Ed25519 key pair...")
    private_key = Ed25519PrivateKey.generate()

    private_key_bytes = private_key.private_bytes_raw()

    # Encrypt private key
    encrypted_key = encrypt_private_key(private_key_bytes, password)

    # Generate SQL
    sql = generate_sql_statement(encrypted_key)

    print()
    print("=" * 60)
    print("GENERATED SQL STATEMENT:")
    print("=" * 60)
    print(sql)
    print()

    print("=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. Run the SQL statement above against your database")
    print("2. Set SERVER_PRIVATE_KEY_PASSWORD environment variable with the password")
    print("3. The server will load the private key from the database on startup")
    print("4. Clients will fetch the public key from the /public-key endpoint")


if __name__ == "__main__":
    main()
