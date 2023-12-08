import hashlib
import secrets


def hash_password(password, salt):
    """
    Hash a password combined with a salt using SHA-256.

    Parameters:
    - password (str): The password to hash.
    - salt (str): The salt to combine with the password.

    Returns:
    - str: The hashed password.
    """
    combined = password + salt
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return hashed


def generate_salt(length=16):
    """
    Generate a random salt of the specified length.

    Parameters:
    - length (int): The length of the salt. Default is 16.

    Returns:
    - str: A random salt.
    """
    salt = secrets.token_hex(length // 2)
    return salt


def generate_sessid(length=32):
    """
    Generate a random session ID of the specified length.

    Parameters:
    - length (int): The length of the session ID. Default is 32.

    Returns:
    - str: A random session ID.
    """
    sessid = secrets.token_hex(length // 2)
    return sessid
