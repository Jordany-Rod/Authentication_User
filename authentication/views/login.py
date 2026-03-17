from django.contrib.messages import success
from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import LoginSerializer, UserSerializer
from ..utils.tokens import TokenManager
from authentication.models import User


class LoginView(APIView):
    """View для входа пользователя"""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Обработка POST запроса на вход"""

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Генерируем токены
            access_token, _ = TokenManager.generate_access_token(user.id)
            refresh_token, _ = TokenManager.generate_refresh_token(user.id)

            # Данные пользователя
            user_data = UserSerializer(user).data

            return Response({
                'success': True,
                'message': 'Вход выполнен успешно',
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token,
                },
                'user': user_data
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    """View для обновления access токена"""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Получение нового access токена по refresh токену"""

        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Refresh token обязателен'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем refresh токен
        user_id = TokenManager.verify_access_token(refresh_token)

        if not user_id:
            return Response({
                'success': False,
                'error': 'Невалидный или истекший refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Пользователь не найден или деактивирован'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Генерируем новый access токен
        new_access_token, _ = TokenManager.generate_access_token(user.id)

        return Response({
            'success': True,
            'access_token': new_access_token
        }, status=status.HTTP_200_OK)