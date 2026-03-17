from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from authentication.serializers import UserSerializer

class ProtectedView(APIView):
    """Тестовое защищенное view для демонстрации работы middleware"""

    def get(self, request):
        """Возвращает данные текущего пользователя"""

        user = request.user
        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Не авторизован'
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'message': 'Доступ разрешен',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

class AdminOnlyView(APIView):
    """Тестовое view только для администратора"""

    def get(self, request):
        user = request.user

        if not user or not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Не авторизован'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_staff:
            return Response({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора'
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'success': True,
            'message': 'Добро пожаловать, администратор!',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

