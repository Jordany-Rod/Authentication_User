from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Post, Comment, Product, Order, OrderItem
from .serializers import (
    CategorySerializer, PostSerializer, CommentSerializer,
    ProductSerializer, OrderSerializer, OrderItemSerializer
)
from authentication.permissions import IsOwnerOrAdmin
from authentication.permission_checker import PermissionChecker


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet для категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов с проверкой прав"""
    queryset = Post.objects.all().select_related('author', 'category')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views_count', 'title']

    def get_queryset(self):
        """Фильтрация постов в зависимости от прав"""
        user = self.request.user

        # Админ видит все
        if user.is_staff:
            return self.queryset

        # Обычный пользователь видит только опубликованные и свои черновики
        return self.queryset.filter(
            Q(status='published') | Q(author=user)
        )

    def perform_create(self, serializer):
        """Создание поста с текущим пользователем как автором"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Обновление поста с проверкой прав через PermissionChecker"""
        post = self.get_object()
        if not PermissionChecker.has_permission(
                self.request.user,
                'post',
                'update',
                post
        ):
            self.permission_denied(self.request)
        serializer.save()

    def perform_destroy(self, instance):
        """Удаление поста с проверкой прав"""
        if not PermissionChecker.has_permission(
                self.request.user,
                'post',
                'delete',
                instance
        ):
            self.permission_denied(self.request)
        instance.delete()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Публикация поста (только для автора или админа)"""
        post = self.get_object()

        if not (request.user.is_staff or post.author == request.user):
            return Response(
                {'error': 'Только автор или администратор может опубликовать пост'},
                status=status.HTTP_403_FORBIDDEN
            )

        post.status = 'published'
        post.save()
        return Response({'status': 'post published'})


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев"""
    queryset = Comment.objects.all().select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['post', 'author']
    search_fields = ['content']

    def get_queryset(self):
        """Пользователи видят все комментарии к доступным постам"""
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        comment = self.get_object()
        if not (self.request.user.is_staff or comment.author == self.request.user):
            self.permission_denied(self.request)
        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or instance.author == self.request.user):
            self.permission_denied(self.request)
        instance.delete()


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для товаров"""
    queryset = Product.objects.all().select_related('seller', 'category')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']

    def get_queryset(self):
        """Проверка прав на просмотр товаров"""
        user = self.request.user

        # Проверяем через PermissionChecker
        if not PermissionChecker.has_permission(user, 'product', 'read'):
            return Product.objects.none()

        return self.queryset

    def perform_create(self, serializer):
        if not PermissionChecker.has_permission(self.request.user, 'product', 'create'):
            self.permission_denied(self.request)
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        product = self.get_object()
        if not PermissionChecker.has_permission(
                self.request.user,
                'product',
                'update',
                product
        ):
            self.permission_denied(self.request)
        serializer.save()

    def perform_destroy(self, instance):
        if not PermissionChecker.has_permission(
                self.request.user,
                'product',
                'delete',
                instance
        ):
            self.permission_denied(self.request)
        instance.delete()


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для заказов"""
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        """Пользователи видят только свои заказы, админы - все"""
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        """Создание заказа с текущим пользователем и нулевой суммой"""
        serializer.save(
            user=self.request.user,
            total_price=0
        )

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Добавление товара в заказ"""
        order = self.get_object()

        if order.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие
        if product.stock < quantity:
            return Response(
                {'error': 'Недостаточно товара на складе'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем позицию заказа
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        # Обновляем общую сумму заказа
        order.total_price += product.price * quantity
        order.save()

        # Уменьшаем количество на складе
        product.stock -= quantity
        product.save()

        serializer = OrderItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)