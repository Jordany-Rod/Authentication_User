from rest_framework import serializers
from authentication.models import (User, BlacklistedToken, Role, Resource,
                                   Action, Permission, UserRole, UserDirectPermission, Condition)
from .utils import PasswordHasher

class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError('Email и пароль обязательны')

        try:
            # Ищем пользователя по email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный email или пароль')

        # Проверяем активен ли пользователь
        if not user.check_password(password):
            raise serializers.ValidationError('Неверный email или пароль')

        # Сохраняем пользователя в validated_data для использования в view
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей"""

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Пароль')
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'},
                                      label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'patronymic', 'password', 'password2']

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        """Проверка уникальности email"""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пльзователь с таким email уже существует')
        return value

    def validate(self, data):
        """Проверка совпадения паролей"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return data

    def create(self, validated_data):
        """Создание нового пользователя"""

        # Удаляем password2 из данных
        validated_data.pop('password2')
        password = validated_data.pop('password')

        # Хешируем пароль через хешер
        hashed_password = PasswordHasher.hash_password(password)

        # Создаем пользователя
        user = User.objects.create(password=hashed_password, **validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'patronymic', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic']

    def validate_first_name(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError('Имя не может быть пустым')
        return value

    def validate_last_name(self, value):
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError('Фамилия не может быть пустой')
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'Новые пароли не совпадают'
            })

        # Валидация сложности пароля
        if len(data['new_password']) < 6:
            raise serializers.ValidationError({
                'new_password': 'Пароль должен быть не менее 6 символов'
            })

        return data

class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для ролей"""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class ResourceSerializer(serializers.ModelSerializer):
    """Сериализатор для ресурсов"""
    class Meta:
        model = Resource
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class ActionSerializer(serializers.ModelSerializer):
    """Сериализатор для действий"""
    class Meta:
        model = Action
        fields = ['id', 'code', 'description']
        read_only_fields = ['id']


class PermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для разрешений"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    action_code = serializers.CharField(source='action.code', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'role', 'role_name', 'resource', 'resource_name',
                  'action', 'action_code', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для назначения ролей пользователям"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_email', 'role', 'role_name',
                  'assigned_at', 'assigned_by']
        read_only_fields = ['id', 'assigned_at']


class UserDirectPermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для прямых разрешений пользователей"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    action_code = serializers.CharField(source='action.code', read_only=True)

    class Meta:
        model = UserDirectPermission
        fields = ['id', 'user', 'user_email', 'resource', 'resource_name',
                  'action', 'action_code', 'is_granted', 'created_at']
        read_only_fields = ['id', 'created_at']

class ConditionSerializer(serializers.ModelSerializer):
    """Сериализатор для условий"""
    class Meta:
        model = Condition
        fields = ['id', 'permission', 'user_permission', 'condition_type',
                  'condition_value', 'created_at']
        read_only_fields = ['id', 'created_at']
