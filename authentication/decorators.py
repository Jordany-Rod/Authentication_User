from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .permission_checker import PermissionChecker


def permission_required(resource_code, action_code):
    """
    Декоратор для проверки прав доступа к ресурсу

    Args:
        resource_code: код ресурса (например, 'post')
        action_code: код действия (например, 'update')

    Пример использования:
        @permission_required('post', 'create')
        def post(self, request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view_instance, request, *args, **kwargs):
            # Получаем экземпляр ресурса, если есть (например, по pk из kwargs)
            resource_instance = None
            resource_pk = kwargs.get('pk')

            if not PermissionChecker.has_permission(
                    request.user,
                    resource_code,
                    action_code,
                    resource_instance
            ):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator

def permission_required_obj(resource_code, action_code, get_obj_func):
    """
    Декоратор для проверки прав с кастомной функцией получения объекта

    Args:
        resource_code: код ресурса
        action_code: код действия
        get_obj_func: функция для получения объекта по kwargs

    Пример:
        @permission_required_obj('post', 'update', lambda k: Post.objects.get(pk=k['pk']))
        def update(self, request, pk=None):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view_instance, request, *args, **kwargs):
            resource_instance = get_obj_func(kwargs) if get_obj_func else None

            if not PermissionChecker.has_permission(
                    request.user,
                    resource_code,
                    action_code,
                    resource_instance
            ):
                return Response(
                    {'error': 'Доступ запрещен'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator
