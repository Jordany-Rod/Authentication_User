from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User, Role, Resource, Action, Permission, UserRole
from business.models import Post


class BusinessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='author@example.com',
            password='securepassword123',
            first_name='Автор',
            last_name='Постов'
        )

        # Создаём роли и права для создания поста
        self.role = Role.objects.create(name='user', description='Обычный пользователь')
        self.resource_post = Resource.objects.create(name='post')
        self.action_create = Action.objects.create(code='create')
        self.action_read = Action.objects.create(code='read')

        Permission.objects.create(role=self.role, resource=self.resource_post, action=self.action_create)
        Permission.objects.create(role=self.role, resource=self.resource_post, action=self.action_read)

        UserRole.objects.create(user=self.user, role=self.role)

    def get_token(self):
        login_res = self.client.post('/api/auth/login/', {
            'email': 'author@example.com', 'password': 'securepassword123'
        }, format='json')
        return login_res.data['tokens']['access']

    def test_create_post_unauthorized(self):
        """Тест 1: Создание поста без токена запрещено (401)"""
        response = self.client.post('/api/business/posts/', {
            'title': 'Новый пост',
            'content': 'Текст поста',
            'status': 'draft'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_authorized(self):
        """Тест 2: Создание поста с токеном и правами разрешено (201)"""
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.post('/api/business/posts/', {
            'title': 'Новый пост',
            'content': 'Текст поста',
            'status': 'draft'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().author, self.user)