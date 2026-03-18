from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from  rest_framework import status
from .utils.tokens import TokenManager
from .models import User
from .permission_checker import PermissionChecker

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

class PermissionCheckMiddleware(MiddlewareMixin):
    """Middleware для проверки прав доступа к ресурсам"""

    # Словарь: путь -> (ресурс, действие)
    # Можно расширить или вынести в БД
    PATH_PERMISSIONS = {
        # Профиль пользователя
        '/api/auth/profile/': ('user', 'update'),
        '/api/auth/change-password/': ('user', 'update'),
        '/api/auth/delete-account/': ('user', 'delete'),

        # Тестовые ресурсы
        '/api/posts/': ('post', 'read'),
        '/api/posts/create/': ('post', 'create'),
        '/api/posts/update/': ('post', 'update'),
        '/api/posts/delete/': ('post', 'delete'),

        '/api/comments/': ('comment', 'read'),
        '/api/comments/create/': ('comment', 'create'),

        '/api/products/': ('product', 'read'),
        '/api/products/create/': ('product', 'create'),
        '/api/products/update/': ('product', 'update'),
        '/api/products/delete/': ('product', 'delete'),

        # Админские пути
        '/api/admin/': ('admin', 'manage'),
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Проверяет права перед вызовом view
        """
        # Если пользователь не аутентифицирован (нет в request) - пропускаем,
        # так как 401 уже должен был вернуть TokenAuthMiddleware
        if not hasattr(request, 'user') or not request.user:
            return None

        # Суперпользователь пропускается
        if request.user.is_superuser:
            return None

        # Получаем путь запроса
        path = request.path_info

        # Ищем соответствие пути с требуемыми правами
        required_permission = None
        for pattern, (resource, action) in self.PATH_PERMISSIONS.items():
            if path.startswith(pattern):
                required_permission = (resource, action)
                break

        # Если для пути не требуются особые права - пропускаем
        if not required_permission:
            return None

        resource_code, action_code = required_permission

        # Получаем ID ресурса из kwargs если есть (для проверки owner_only)
        resource_id = view_kwargs.get('pk')

        # Получаем экземпляр ресурса если нужно
        resource_instance = None
        if resource_id and resource_code in ['post', 'comment', 'product']:
            # Здесь можно динамически загружать объект
            # Для демо пропускаем, будем проверять в самом view
            pass

        # Проверяем права
        if not PermissionChecker.has_permission(
                request.user,
                resource_code,
                action_code,
                resource_instance
        ):
            return JsonResponse({
                'success': False,
                'error': 'Доступ запрещен',
                'code': 'permission_denied',
                'required': f'{action_code} on {resource_code}'
            }, status=status.HTTP_403_FORBIDDEN)

        return None

class DisableCSRFMiddleware(MiddlewareMixin):
    """Отключает CSRF проверку для API запросов"""

    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None