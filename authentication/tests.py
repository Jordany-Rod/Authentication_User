from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User, Role, Resource, Action, Permission, UserRole


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_data = {
            'email': 'test@example.com',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password': 'securepassword123',
            'password2': 'securepassword123'
        }

        # Создаём роль и права для доступа к профилю
        self.role = Role.objects.create(name='user', description='Обычный пользователь')
        self.resource_user = Resource.objects.create(name='user')
        self.action_update = Action.objects.create(code='update')
        self.action_delete = Action.objects.create(code='delete')

        Permission.objects.create(role=self.role, resource=self.resource_user, action=self.action_update)
        Permission.objects.create(role=self.role, resource=self.resource_user, action=self.action_delete)

    def test_register_user(self):
        """Тест 1: Успешная регистрация пользователя"""
        response = self.client.post('/api/auth/register/', self.register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_login_get_tokens(self):
        """Тест 2: Вход в систему и получение JWT токенов"""
        self.client.post('/api/auth/register/', self.register_data, format='json')
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com', 'password': 'securepassword123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_profile_without_token(self):
        """Тест 3: Доступ к профилю без токена запрещён (401)"""
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json().get('code'), 'token_missing')

    def test_profile_with_token(self):
        """Тест 4: Доступ к профилю с валидным токеном разрешён (200)"""
        self.client.post('/api/auth/register/', self.register_data, format='json')
        login_res = self.client.post('/api/auth/login/', {
            'email': 'test@example.com', 'password': 'securepassword123'
        }, format='json')

        token = login_res.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # Назначаем роль пользователю
        user = User.objects.get(email='test@example.com')
        UserRole.objects.create(user=user, role=self.role)

        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_change_password(self):
        """Тест 5: Смена пароля"""
        self.client.post('/api/auth/register/', self.register_data, format='json')
        login_res = self.client.post('/api/auth/login/', {
            'email': 'test@example.com', 'password': 'securepassword123'
        }, format='json')
        token = login_res.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        user = User.objects.get(email='test@example.com')
        UserRole.objects.create(user=user, role=self.role)

        response = self.client.post('/api/auth/change-password/', {
            'old_password': 'securepassword123',
            'new_password': 'newsecurepassword123',
            'new_password2': 'newsecurepassword123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_account(self):
        """Тест 6: Мягкое удаление аккаунта (деактивация)"""
        self.client.post('/api/auth/register/', self.register_data, format='json')
        login_res = self.client.post('/api/auth/login/', {
            'email': 'test@example.com', 'password': 'securepassword123'
        }, format='json')
        token = login_res.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        user = User.objects.get(email='test@example.com')
        UserRole.objects.create(user=user, role=self.role)

        response = self.client.delete('/api/auth/delete-account/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertFalse(user.is_active)