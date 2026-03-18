from django.core.management.base import BaseCommand
from authentication.models import (
    User, Role, Resource, Action, Permission,
    UserRole, UserDirectPermission, Condition
)


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для системы прав'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных для системы прав...')

        # 1. Создаем действия
        actions_data = [
            {'code': 'create', 'description': 'Создание'},
            {'code': 'read', 'description': 'Чтение'},
            {'code': 'update', 'description': 'Обновление'},
            {'code': 'delete', 'description': 'Удаление'},
            {'code': 'manage', 'description': 'Управление'},
        ]

        actions = {}
        for data in actions_data:
            action, created = Action.objects.get_or_create(
                code=data['code'],
                defaults={'description': data['description']}
            )
            actions[data['code']] = action
            if created:
                self.stdout.write(f"  Создано действие: {data['code']}")

        # 2. Создаем ресурсы
        resources_data = [
            {'name': 'post', 'description': 'Посты блога'},
            {'name': 'comment', 'description': 'Комментарии'},
            {'name': 'user', 'description': 'Профили пользователей'},
            {'name': 'product', 'description': 'Товары (для демо)'},
        ]

        resources = {}
        for data in resources_data:
            resource, created = Resource.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            resources[data['name']] = resource
            if created:
                self.stdout.write(f"  Создан ресурс: {data['name']}")

        # 3. Создаем роли
        roles_data = [
            {'name': 'admin', 'description': 'Полный доступ ко всем ресурсам'},
            {'name': 'manager', 'description': 'Управление контентом'},
            {'name': 'user', 'description': 'Обычный пользователь'},
            {'name': 'guest', 'description': 'Анонимный пользователь'},
        ]

        roles = {}
        for data in roles_data:
            role, created = Role.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            roles[data['name']] = role
            if created:
                self.stdout.write(f"  Создана роль: {data['name']}")

        # 4. Назначаем разрешения для ролей

        # Admin - все на все
        for resource in resources.values():
            for action in actions.values():
                Permission.objects.get_or_create(
                    role=roles['admin'],
                    resource=resource,
                    action=action
                )

        # Manager - чтение и обновление постов и комментариев
        manager_perms = [
            (resources['post'], actions['read']),
            (resources['post'], actions['update']),
            (resources['comment'], actions['read']),
            (resources['comment'], actions['update']),
            (resources['product'], actions['read']),
            (resources['product'], actions['update']),
        ]

        for resource, action in manager_perms:
            Permission.objects.get_or_create(
                role=roles['manager'],
                resource=resource,
                action=action
            )

        # User - базовые права
        user_perms = [
            (resources['post'], actions['create']),
            (resources['post'], actions['read']),
            (resources['post'], actions['update']),  # с условием owner_only
            (resources['comment'], actions['create']),
            (resources['comment'], actions['read']),
            (resources['comment'], actions['update']),  # с условием owner_only
            (resources['user'], actions['read']),
            (resources['user'], actions['update']),  # только свой профиль
        ]

        for resource, action in user_perms:
            perm, created = Permission.objects.get_or_create(
                role=roles['user'],
                resource=resource,
                action=action
            )

            # Добавляем условие owner_only для update
            if action.code == 'update' and resource.name in ['post', 'comment', 'user']:
                Condition.objects.get_or_create(
                    permission=perm,
                    condition_type='owner_only',
                    condition_value={}
                )

        # Guest - только чтение
        guest_perms = [
            (resources['post'], actions['read']),
            (resources['comment'], actions['read']),
            (resources['product'], actions['read']),
        ]

        for resource, action in guest_perms:
            Permission.objects.get_or_create(
                role=roles['guest'],
                resource=resource,
                action=action
            )

        # 5. Назначаем роли существующим пользователям
        try:
            admin_user = User.objects.get(email='admin@example.com')
            UserRole.objects.get_or_create(
                user=admin_user,
                role=roles['admin']
            )
            self.stdout.write(f"  Роль admin назначена пользователю {admin_user.email}")
        except User.DoesNotExist:
            pass

        try:
            test_user = User.objects.get(email='newuser@test.com')
            UserRole.objects.get_or_create(
                user=test_user,
                role=roles['user']
            )
            self.stdout.write(f"  Роль user назначена пользователю {test_user.email}")
        except User.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))