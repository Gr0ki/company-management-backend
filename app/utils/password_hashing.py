from ..core.settings import get_settings


settings = get_settings()

def hash_password(password: str) -> str:
    return settings.pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return settings.pwd_context.verify(password, hashed_password)