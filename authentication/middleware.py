from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from  rest_framework import status
from .utils.tokens import TokenManager
from .models import User

class TokenAuthMiddleware(MiddlewareMixin):
    """Middleware для аутентификации по JWT токену"""

    # Список путей, которые не требуют аутентификации

    PUBLIC_PATHS = [
        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/refresh/',
        '/admin/',
    ]

    def process_request(self, request):
        """Обрабатывает запрос до того, как он попадет в view"""

        # Пропускает публичные пути
        path = request.path_info
        if any(path.startswith(public_path) for public_path in self.PUBLIC_PATHS):
            return None

        # Получаем токен из заголовка Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'error': 'Токен не предоставлен или неверный формат',
                'code': 'token_missing'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Извлекаем токен
        token = auth_header.split(' ')[1]

        # Проверяем токен
        user_id = TokenManager.verify_access_token(token)

        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'Невалидный или истекший токен',
                'code': 'token_invalid'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем пользователя из БД
        try:
            user = User.objects.get(id=user_id, is_active=True)
            # Добавляем пользователя в request для использования в views
            request.user = user
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Пользователь не найден или деактивирован',
                'code': 'user_not_found'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return None
