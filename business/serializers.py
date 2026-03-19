from rest_framework import serializers
from .models import Category, Post, Comment, Product, Order, OrderItem
from authentication.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'author_email', 'author_name',
            'category', 'category_name', 'status', 'views_count',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'views_count', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name()


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'post_title', 'author', 'author_email', 'author_name',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name()


class ProductSerializer(serializers.ModelSerializer):
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    seller_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'seller', 'seller_email', 'seller_name',
            'category', 'category_name', 'stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['seller', 'created_at', 'updated_at']

    def get_seller_name(self, obj):
        return obj.seller.get_full_name()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'user_name', 'items', 'items_count',
            'total_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_price', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name()

