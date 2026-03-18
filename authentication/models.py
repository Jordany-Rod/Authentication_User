from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .utils import PasswordHasher

class CustomUserManager(BaseUserManager):
    """Менеджер для создания пользователей и суперпользователей"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет обычного пользователя"""

        if not email:
            raise ValueError('Email обязателен')

        # Приводим email к нижнему регистру
        email = self.normalize_email(email)

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        # Создаем пользователя без пароля (временно)
        user = self.model(email=email, **extra_fields)

        # Используем хешер
        if password:
            user.password = PasswordHasher.hash_password(password)
        else:
            user.password = PasswordHasher.hash_password('')

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя (админ)"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""

    email = models.EmailField(unique=True, db_index=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=150, blank=True, verbose_name='Отчество')

    # Технические поля
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    # Статусы
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')

    # Указываем менеджер объектов
    objects = CustomUserManager()

    # Поле для входа
    USERNAME_FIELD = 'email'

    # Поля обязательные для создания суперпользователя
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        """Строковое представление"""

        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        """Полное имя"""

        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self):
        """Короткое имя"""

        return self.first_name

    # Метод проверки пароля
    def check_password(self, raw_password):
        """Проверяет пароль используя хешер"""

        return PasswordHasher.verify_password(raw_password, self.password)

    def set_password(self, raw_password):
        """Устанавливает пароль используя хешер"""

        self.password = PasswordHasher.hash_password(raw_password)

class BlacklistedToken(models.Model):
    """Модель для хранения отозванных токенов (для logout)"""

    token = models.TextField(unique=True, db_index=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')

    class Meta:
        db_table = 'blacklisted_tokens'
        verbose_name = 'Отзывной токен'
        verbose_name_plural = 'Отзывные токены'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Token for {self.user.email} blacklisted at {self.blacklisted_at}"

class Role(models.Model):
    """Модель роли пользователя"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name

class Resource(models.Model):
    """Модель ресурса (объекта доступа)"""

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'resources'
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'
        ordering = ['name']

    def __str__(self):
        return self.name

class Action(models.Model):
    """Модель действия (CRUD + дополнительные)"""

    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('read', 'Чтение'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('manage', 'Управление'),
    ]

    code = models.CharField(max_length=20, unique=True, choices=ACTION_CHOICES, verbose_name='Код')
    description = models.CharField(max_length=100, blank=True, verbose_name='Описание')

    class Meta:
        db_table = 'actions'
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'
        ordering = ['code']

    def __str__(self):
        return self.get_code_display()

class Permission(models.Model):
    """Модель разрешения (связь Роль-Ресурс-Действие)"""

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions', verbose_name='Роль')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='permissions', verbose_name='Ресурс')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='permissions', verbose_name='Действие')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'permissions'
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        unique_together = ['role', 'resource', 'action']
        indexes = [
            models.Index(fields=['role', 'resource', 'action']),
        ]

    def __str__(self):
        return f"{self.role} - {self.resource} - {self.action}"

class UserRole(models.Model):
    """Модель назначения ролей пользователям"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_roles', verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Роль')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата назначения')
    assigned_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_roles', verbose_name='Кем назначен')

    class Meta:
        db_table = 'user_roles'
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ['user', 'role']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

class UserDirectPermission(models.Model):
    """Модель прямых разрешений для пользователей (override)"""

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='direct_permissions',
                             verbose_name='Пользователь')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name='Ресурс')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, verbose_name='Действие')
    is_granted = models.BooleanField(default=True, verbose_name='Разрешено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'user_direct_permissions'
        verbose_name = 'Прямое разрешение'
        verbose_name_plural = 'Прямые разрешения'
        unique_together = ['user', 'resource', 'action']

    def __str__(self):
        status = 'разрешено' if self.is_granted else 'запрещено'
        return f"{self.user.email} - {self.resource} - {self.action} ({status})"

class Condition(models.Model):
    """Модель условий для ABAC (атрибутный контроль доступа)"""

    CONDITION_TYPES = [
        ('owner_only', 'Только владелец'),
        ('status', 'Статус ресурса'),
        ('date_range', 'Диапазон дат'),
        ('custom', 'Пользовательское условие'),
    ]

    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='conditions', null=True, blank=True,
                                  verbose_name='Разрешение')
    user_permission = models.ForeignKey(UserDirectPermission, on_delete=models.CASCADE, related_name='conditions',
                                       null=True, blank=True, verbose_name='Прямое разрешение')
    condition_type = models.CharField(max_length=50, choices=CONDITION_TYPES, verbose_name='Тип условия')
    condition_value = models.TextField(default='{}', verbose_name='Значение условия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'conditions'
        verbose_name = 'Условие'
        verbose_name_plural = 'Условия'

    def __str__(self):
        return f"{self.get_condition_type_display()}: {self.condition_value}"
