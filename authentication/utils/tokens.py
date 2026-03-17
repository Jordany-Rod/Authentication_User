import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from ..models import BlacklistedToken

class TokenManager:
    """Класс для работы с JWT токенами"""

    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @classmethod
    def generate_access_token(cls, user_id):
        """Генерация access токена"""

        exp_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            'user_id': user_id,
            'token_type': 'access',
            'exp': exp_time,
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token, exp_time

    @classmethod
    def generate_refresh_token(cls, user_id):
        """Генерация refresh токена"""

        exp_time = datetime.datetime.utcnow() + datetime.timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            'user_id': user_id,
            'token_type': 'refresh',
            'exp': exp_time,
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return token, exp_time

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
        """Проверка access токена и получение user_id учитывает Blacklist"""

        # Проверяем, не в черном ли списке токен

        if BlacklistedToken.objects.filter(token=token).exists():
            return None

        payload = cls.decode_token(token)
        if payload and payload.get('token_type') == 'access':
            return payload.get('user_id')
        return None

    @classmethod
    def blacklist_token(cls, token, user):
        """Добавляет токен в черный список (logout)"""

        payload = cls.decode_token(token)
        if not payload:
            return False

        # Получаем время истечения токена
        exp_timestamp = payload.get('exp')
        if exp_timestamp:
            expires_at = datetime.datetime.fromtimestamp(exp_timestamp, tz=datetime.timezone.utc)
        else:
            expires_at = timezone.now() + datetime.timedelta(days=1)

        # Создаем запись в черном списке
        BlacklistedToken.objects.get_or_create(
            token=token,
            defaults={
                'user': user,
                'expires_at': expires_at
            }
        )
        return True

    @classmethod
    def clean_expired_tokens(cls):
        """
        Очищает истекшие токены из черного списка
        Можно вызывать периодически через cron или celery
        """
        BlacklistedToken.objects.filter(expires_at__lt=timezone.now()).delete()


