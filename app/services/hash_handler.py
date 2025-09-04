from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash


ph = PasswordHasher(
    time_cost=2, memory_cost=32768, parallelism=8, hash_len=32, salt_len=16
)


def get_hash(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("Password must be a str")
    return ph.hash(password)


def is_hash_eq(input_hash: str, db_hash: str) -> bool:
    if not isinstance(input_hash, str) or not isinstance(db_hash, str):
        raise TypeError("Password and hashed must be str")
    try:
        return ph.verify(db_hash, input_hash)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False
