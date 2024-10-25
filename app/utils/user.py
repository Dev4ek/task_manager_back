import bcrypt

async def hash_password(plain_password: str) -> str:
    """
    Хеширует предоставленный пароль с использованием bcrypt.

    Args:
        plain_password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

async def check_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли предоставленный пароль с хешированным паролем.

    Args:
        plain_password (str): Пароль для проверки.
        hashed_password (str): Хешированный пароль, с которым производится сравнение.

    Returns:
        bool: True, если пароли совпадают, False - в противном случае.
    """
    
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
