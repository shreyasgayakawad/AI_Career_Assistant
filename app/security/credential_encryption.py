"""
Credential Encryption Utilities

Provides Fernet encryption and decryption for sensitive
external credentials such as OAuth access tokens.
"""

from cryptography.fernet import Fernet, InvalidToken

from app.config.settings import CREDENTIAL_ENCRYPTION_KEY


def _get_fernet() -> Fernet:
    """
    Create a Fernet cipher using the application encryption key.
    """

    try:
        return Fernet(
            CREDENTIAL_ENCRYPTION_KEY.encode(),
        )
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "CREDENTIAL_ENCRYPTION_KEY is invalid."
        ) from exc


def encrypt_credential(
    credential: str,
) -> str:
    """
    Encrypt a sensitive credential.

    Returns the encrypted credential as a string.
    """

    if not credential:
        raise ValueError(
            "Credential cannot be empty."
        )

    encrypted = _get_fernet().encrypt(
        credential.encode(),
    )

    return encrypted.decode()


def decrypt_credential(
    encrypted_credential: str,
) -> str:
    """
    Decrypt a previously encrypted credential.

    Raises ValueError if the credential cannot be decrypted.
    """

    if not encrypted_credential:
        raise ValueError(
            "Encrypted credential cannot be empty."
        )

    try:
        decrypted = _get_fernet().decrypt(
            encrypted_credential.encode(),
        )
    except InvalidToken as exc:
        raise ValueError(
            "Invalid or corrupted encrypted credential."
        ) from exc

    return decrypted.decode()