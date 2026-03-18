from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import (
    User, Role, Resource, Action, Permission,
    UserRole, UserDirectPermission, Condition
)
from ..serializers import (
    RoleSerializer, ResourceSerializer, ActionSerializer,
    PermissionSerializer, UserRoleSerializer,
    UserDirectPermissionSerializer, ConditionSerializer,
    UserSerializer
)
from ..permissions import IsAdminUser, IsSuperUser

class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ролями (только для администраторов)"""
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ресурсами (только для администраторов)"""
    queryset = Resource.objects.all().order_by('name')
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class ActionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления действиями (только для администраторов)"""
    queryset = Action.objects.all().order_by('code')
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления разрешениями (только для администраторов)"""
    queryset = Permission.objects.all().select_related('role', 'resource', 'action')
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=True, methods=['get', 'post'])
    def conditions(self, request, pk=None):
        """Управление условиями для конкретного разрешения"""
        permission = self.get_object()

        if request.method == 'GET':
            conditions = permission.conditions.all()
            serializer = ConditionSerializer(conditions, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ConditionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(permission=permission)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet для назначения ролей пользователям"""
    queryset = UserRole.objects.all().select_related('user', 'role')
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

class UserDirectPermissionViewSet(viewsets.ModelViewSet):
    """ViewSet для управления прямыми разрешениями пользователей"""
    queryset = UserDirectPermission.objects.all().select_related('user', 'resource', 'action')
    serializer_class = UserDirectPermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра пользователей администратором"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Назначение роли пользователю"""
        user = self.get_object()
        role_id = request.data.get('role_id')

        if not role_id:
            return Response(
                {'error': 'role_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Роль не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )

        if created:
            return Response(
                {'message': f'Роль {role.name} назначена пользователю {user.email}'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Роль уже назначена'},
                status=status.HTTP_200_OK
            )

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Удаление роли у пользователя"""
        user = self.get_object()
        role_id = request.data.get('role_id')

        if not role_id:
            return Response(
                {'error': 'role_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count = UserRole.objects.filter(user=user, role_id=role_id).delete()[0]

        if deleted_count:
            return Response(
                {'message': 'Роль удалена'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Роль не найдена у пользователя'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Получение всех прав пользователя"""
        user = self.get_object()
        from ..permission_checker import PermissionChecker

        # Получаем все ресурсы и действия
        resources = Resource.objects.all()
        actions = Action.objects.all()

        result = []
        for resource in resources:
            resource_perms = []
            for action in actions:
                has_perm = PermissionChecker.has_permission(user, resource.name, action.code)
                if has_perm:
                    resource_perms.append(action.code)

            if resource_perms:
                result.append({
                    'resource': resource.name,
                    'actions': resource_perms
                })

        return Response(result)

