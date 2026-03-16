from django.core.serializers import serialize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers import RegisterSerializer, UserSerializer

class RegisterView(APIView):
    """View для регистрации новых пользователей"""

    authentication_classes = [] # Отключаем аутентификацию для регистрации
    permission_classes = [] # Отключаем проверку прав

    def post(self, request):
        """Обработка POST запроса на регистрацию"""

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            # Создаем пользователя
            user = serializer.save()

            # Возвращаем данные пользователя (без пароля)
            user_data = UserSerializer(user).data
            return Response ({
                'success': True,
                'message': 'Пользователь успешно зарегистрирован',
                'user': user_data
            }, status=status.HTTP_201_CREATED)

        # Если данные невалидны, возвращаем ошибки
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
