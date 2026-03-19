from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from business.models import Category, Post, Comment, Product, Order, OrderItem
from authentication.models import User
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми бизнес-данными'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых бизнес-данных...')

        # Получаем или создаем пользователей
        users = list(User.objects.all())
        if len(users) < 3:
            # Создаем дополнительных пользователей если нужно
            for i in range(3):
                user, created = User.objects.get_or_create(
                    email=f'testuser{i}@example.com',
                    defaults={
                        'first_name': f'Тест{i}',
                        'last_name': 'Пользователь',
                        'is_active': True
                    }
                )
                if created:
                    user.set_password('testpass123')
                    user.save()
                    users.append(user)

        # Категории
        categories_data = [
            {'name': 'Новости', 'description': 'Новости и события'},
            {'name': 'Технологии', 'description': 'IT и технологии'},
            {'name': 'Наука', 'description': 'Научные статьи'},
            {'name': 'Искусство', 'description': 'Искусство и культура'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(cat)
            if created:
                self.stdout.write(f"  Создана категория: {cat.name}")

        # Посты
        posts_data = [
            {'title': 'Первая новость', 'content': 'Содержание первой новости...', 'status': 'published'},
            {'title': 'Новая технология', 'content': 'Описание новой технологии...', 'status': 'published'},
            {'title': 'Научное открытие', 'content': 'Описание открытия...', 'status': 'draft'},
            {'title': 'Выставка современного искусства', 'content': 'Обзор выставки...', 'status': 'published'},
        ]

        posts = []
        for i, post_data in enumerate(posts_data):
            post, created = Post.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'author': random.choice(users),
                    'category': random.choice(categories) if random.choice([True, False]) else None,
                    'status': post_data['status'],
                    'views_count': random.randint(0, 100)
                }
            )
            posts.append(post)
            if created:
                self.stdout.write(f"  Создан пост: {post.title}")

        # Комментарии
        comments_data = [
            'Отличный пост!',
            'Спасибо за информацию',
            'Интересная точка зрения',
            'Не совсем согласен',
        ]

        for post in posts[:2]:  # Комментарии только к первым двум постам
            for comment_text in comments_data:
                comment, created = Comment.objects.get_or_create(
                    post=post,
                    content=comment_text,
                    defaults={
                        'author': random.choice(users)
                    }
                )
                if created:
                    self.stdout.write(f"  Создан комментарий к {post.title}")

        # Товары
        products_data = [
            {'name': 'Ноутбук', 'description': 'Мощный ноутбук', 'price': 50000},
            {'name': 'Смартфон', 'description': 'Современный смартфон', 'price': 30000},
            {'name': 'Книга', 'description': 'Интересная книга', 'price': 500},
            {'name': 'Кофеварка', 'description': 'Кофеварка для дома', 'price': 3000},
        ]

        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'seller': random.choice(users),
                    'category': random.choice(categories) if random.choice([True, False]) else None,
                    'stock': random.randint(5, 50)
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f"  Создан товар: {product.name}")

        # Заказы
        for _ in range(3):
            user = random.choice(users)
            order, created = Order.objects.get_or_create(
                user=user,
                total_price=0,
                status='new'
            )
            if created:
                # Добавляем товары в заказ
                for _ in range(random.randint(1, 3)):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    if product.stock >= quantity:
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )
                        order.total_price += product.price * quantity
                        product.stock -= quantity
                        product.save()

                order.save()
                self.stdout.write(f"  Создан заказ #{order.id} на сумму {order.total_price}")

        self.stdout.write(self.style.SUCCESS('Тестовые бизнес-данные успешно созданы!'))
