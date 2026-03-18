from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Разрешение только для администраторов"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsSuperUser(permissions.BasePermission):
    """Разрешение только для суперпользователей"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение для владельца объекта или администратора"""

    def has_object_permission(self, request, view, obj):
        # Администратор имеет доступ ко всему
        if request.user.is_staff:
            return True

        # Проверяем, является ли пользователь владельцем
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id

        return False