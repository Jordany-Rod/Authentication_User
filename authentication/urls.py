from django.urls import path
from .views import (
    RegisterView, LoginView, RefreshTokenView,
    ProtectedView, AdminOnlyView,
    ProfileView, ChangePasswordView, LogoutView,
    LogoutAllView, DeleteAccountView
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
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only')
]

