import jwt
import datetime
from django.conf import settings

class TokenManager:
    """Класс для работы с JWT токенами"""

    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @classmethod
    def generate_access_token(cls, user_id):
        """Генерация access токена"""

        payload = {
            'user_id': user_id,
            'token_type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def generate_refresh_token(cls, user_id):
        """Генерация refresh токена"""

        payload = {
            'user_id': user_id,
            'token_type': 'refresh',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_token(cls, token):
        """Декодирование и проверка токена"""
        try:
            payload = payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

            return payload
        except jwt.ExpiredSignatureError:
            return None # Токен истек
        except jwt.InvalidTokenError:
            return None # Невалидный токен

    @classmethod
    def verify_access_token(cls, token):
        """Проверка access токена и получение user_id"""

        payload = cls.decode_token(token)
        if payload and payload.get('token_type') == 'access':
            return payload.get('user_id')
        return None
