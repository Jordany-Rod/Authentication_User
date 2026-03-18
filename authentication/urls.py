from django.urls import path
from .views import (
    # Аутентификация
    RegisterView, LoginView, RefreshTokenView,
    LogoutView, LogoutAllView,

    # Профиль
    ProfileView, ChangePasswordView, DeleteAccountView,

    # Тестовые
    ProtectedView, AdminOnlyView,

    # Демо-ресурсы
    PostListView, PostCreateView, PostDetailView,
    PostUpdateView, PostDeleteView,
    CommentListView, CommentCreateView,
    ProductListView,
)

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout_all'),

    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    # Тестовые защищенные маршруты
    path('me/', ProtectedView.as_view(), name='me'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),

    # Демо-ресурсы (посты)
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    # Демо-ресурсы (комментарии)
    path('comments/', CommentListView.as_view(), name='comment_list'),
    path('comments/create/', CommentCreateView.as_view(), name='comment_create'),

    # Демо-ресурсы (товары)
    path('products/', ProductListView.as_view(), name='product_list'),
]

