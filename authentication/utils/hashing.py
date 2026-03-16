import hashlib
import os
import base64
import hmac

class PasswordHasher:
    """Кастомный класс для хеширования паролей использует SHA-256 с солью"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль со случайной солью Формат: соль$хеш"""

        # Генерируем случайную соль (32 байта)
        salt = os.urandom(32)

        # Хешируем пароль с солью
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        # Кодируем соль и хеш в base64 для хранения в строке
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        hash_b64 = base64.b64encode(hash_obj).decode('utf-8')

        # Сохраняем соль и хеш через разделитель
        return f"{salt_b64}${hash_b64}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Проверяет соответствует ли пароль хешу"""

        try:
            # Разделяем соль и хеш
            salt_b64, hash_b64 = hashed.split('$')

            # Декодируем из base64
            salt = base64.b64decode(salt_b64.encode('utf-8'))
            original_hash = base64.b64decode(hash_b64.encode('utf-8'))

            # Хешируем введенный пароль с той же солью
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

            return hmac.compare_digest(hash_obj, original_hash)

        except (ValueError, IndexError, TypeError):
            return False