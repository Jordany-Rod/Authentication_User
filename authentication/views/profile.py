from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import (
    UserSerializer, ProfileUpdateSerializer, ChangePasswordSerializer
)
from authentication.utils import PasswordHasher
from authentication.utils.tokens import TokenManager

class ProfileView(APIView):
    """View для получения и обновления профиля пользователя"""

    def get(self, request):
        """Получить данные текущего пользователя"""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request):
        """Обновить данные профиля"""
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Профиль успешно обновлен',
                'user': UserSerializer(request.user).data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """View для смены пароля"""

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Проверяем старый пароль
        if not user.check_password(old_password):
            return Response({
                'success': False,
                'error': 'Невенрый текущий пароль'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()

        return Response({
            'success': True,
            'message': 'Пароль успешно изменен'
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """View для выхода из системы (добавляет токен в черный список)"""

    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Добавляем токен в черный список
            TokenManager.blacklist_token(token, request.user)

        return Response({
            'success': True,
            'message': 'Выход выполнен успешно'
        }, status=status.HTTP_200_OK)

class LogoutAllView(APIView):
    """View для выхода из всех устройств (добавляет все токены пользователя в черный список)"""

    def post(self, request):
        from ..models import BlacklistedToken
        import datetime

        user = request.user

        # Создаем запись в профиле пользователя блокирующую все токены с определенной даты
        user.last_logout_all = datetime.datetime.now()
        user.save()

        return Response({
            'success': True,
            'message': 'Выход из всех устройств выполнен успешно'
        }, status=status.HTTP_200_OK)

class DeleteAccountView(APIView):
    """View для мягкого удаления аккаунта"""

    def delete(self, request):
        user = request.user

        # Мягкое удаление - деактивируем пользователя
        user.is_active = False
        user.save()

        # Также отзываем текущий токен
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            TokenManager.blacklist_token(token, user)

        return Response({
            'success': True,
            'message': 'Аккаунт успешно деактивирован'
        }, status=status.HTTP_200_OK)