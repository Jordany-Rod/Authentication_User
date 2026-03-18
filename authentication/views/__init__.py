from .register import RegisterView
from .login import LoginView, RefreshTokenView
from .protected import ProtectedView, AdminOnlyView
from .profile import ProfileView, ChangePasswordView, LogoutView, LogoutAllView, DeleteAccountView
from .demo_recources import (
    PostListView, PostCreateView, PostDetailView,
    PostUpdateView, PostDeleteView,
    CommentListView, CommentCreateView,
    ProductListView
)
from .admin_views import (
    RoleViewSet, ResourceViewSet, ActionViewSet,
    PermissionViewSet, UserRoleViewSet,
    UserDirectPermissionViewSet, AdminUserViewSet
)


__all__ = [
    'RegisterView', 'LoginView', 'RefreshTokenView',
    'ProtectedView', 'AdminOnlyView',
    'ProfileView', 'ChangePasswordView', 'LogoutView',
    'LogoutAllView', 'DeleteAccountView',
    'ProductListView', 'PostCreateView','PostDetailView',
    'PostUpdateView', 'PostDeleteView',
    'CommentListView', 'CommentCreateView',
    'PostListView',
    'RoleViewSet', 'ResourceViewSet', 'ActionViewSet',
    'PermissionViewSet', 'UserRoleViewSet',
    'UserDirectPermissionViewSet', 'AdminUserViewSet'
]

