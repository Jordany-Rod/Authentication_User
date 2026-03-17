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
