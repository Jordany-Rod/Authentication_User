from django.db.models import Q
from .models import User, Role, Resource, Action, Permission, UserRole, UserDirectPermission, Condition

class PermissionChecker:
    """Класс для проверки прав доступа"""

    @classmethod
    def has_permission(cls, user, resource_code, action_code, resource_instance=None):
        """
        Проверяет, есть ли у пользователя право на выполнение действия над ресурсом

        Args:
            user: объект пользователя
            resource_code: код ресурса (например, 'post')
            action_code: код действия (например, 'update')
            resource_instance: конкретный экземпляр ресурса (для проверки условий)

        Returns:
            bool: True если доступ разрешен, False если запрещен
        """
        if not user or not user.is_authenticated:
            return False

        # Суперпользователь имеет все права
        if user.is_superuser:
            return True

        try:
            resource = Resource.objects.get(name=resource_code)
            action = Action.objects.get(code=action_code)
        except (Resource.DoesNotExist, Action.DoesNotExist):
            return False

        # 1. Проверка прямых запретов
        if cls._has_direct_deny(user, resource, action):
            return False

        # 2. Проверка прямых разрешений
        if cls._has_direct_grant(user, resource, action, resource_instance):
            return True

        # 3. Проверка через роли
        if cls._has_role_permission(user, resource, action, resource_instance):
            return True

        return False

    @classmethod
    def _has_direct_deny(cls, user, resource, action):
        """Проверка прямых запретов"""
        return UserDirectPermission.objects.filter(
            user=user,
            resource=resource,
            action=action,
            is_granted=False
        ).exists()

    @classmethod
    def _has_direct_grant(cls, user, resource, action, resource_instance=None):
        """Проверка прямых разрешений"""
        direct_perms = UserDirectPermission.objects.filter(
            user=user,
            resource=resource,
            action=action,
            is_granted=True
        )

        for perm in direct_perms:
            if cls._check_conditions(perm, user, resource_instance):
                return True

        return False

    @classmethod
    def _has_role_permission(cls, user, resource, action, resource_instance=None):
        """Проверка разрешений через роли"""
        user_roles = UserRole.objects.filter(user=user).values_list('role', flat=True)

        if not user_roles:
            return False

        permissions = Permission.objects.filter(
            role_id__in=user_roles,
            resource=resource,
            action=action
        )

        for perm in permissions:
            if cls._check_conditions(perm, user, resource_instance):
                return True

        return False

    @classmethod
    def _check_conditions(cls, permission_obj, user, resource_instance=None):
        """
        Проверка условий для разрешения

        Args:
            permission_obj: объект Permission или UserDirectPermission
            user: текущий пользователь
            resource_instance: экземпляр ресурса (если есть)

        Returns:
            bool: True если условия выполнены
        """

        # Получаем условия для этого разрешения
        if hasattr(permission_obj, 'conditions'):
            conditions = permission_obj.conditions.all()
        else:
            return True

        if not conditions:
            return True

        # Проверяем каждое условие
        for condition in conditions:
            if not cls._evaluate_condition(condition, user, resource_instance):
                return False

        return True

    @classmethod
    def _evaluate_condition(cls, condition, user, resource_instance=None):
        """
        Вычисление конкретного условия
        """
        cond_type = condition.condition_type
        value = condition.condition_value

        if cond_type == 'owner_only':
            # Проверка, что пользователь - владелец ресурса
            if not resource_instance:
                return False
            return getattr(resource_instance, 'user_id', None) == user.id

        elif cond_type == 'status':
            # Проверка статуса ресурса
            if not resource_instance:
                return False
            required_status = value.get('status')
            if not required_status:
                return True
            return getattr(resource_instance, 'status', None) == required_status

        elif cond_type == 'date_range':
            # Проверка диапазона дат
            from django.utils import timezone
            now = timezone.now()
            start_date = value.get('start')
            end_date = value.get('end')

            if start_date and now < timezone.datetime.fromiso(start_date):
                return False
            if end_date and now > timezone.datetime.fromiso(end_date):
                return False
            return True

        elif cond_type == 'custom':

            return True

        return True