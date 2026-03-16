from rest_framework import serializers
from .models import User
from .utils import PasswordHasher

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

