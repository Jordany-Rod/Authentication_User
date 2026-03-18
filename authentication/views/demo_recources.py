from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from ..decorators import permission_required

# Демо-данные (вместо БД)
posts = [
    {'id': 1, 'title': 'Пост 1', 'content': 'Содержание поста 1', 'user_id': 5, 'status': 'published'},
    {'id': 2, 'title': 'Пост 2', 'content': 'Содержание поста 2', 'user_id': 6, 'status': 'draft'},
    {'id': 3, 'title': 'Пост 3', 'content': 'Содержание поста 3', 'user_id': 5, 'status': 'published'},
]

comments = [
    {'id': 1, 'post_id': 1, 'text': 'Комментарий 1', 'user_id': 6},
    {'id': 2, 'post_id': 1, 'text': 'Комментарий 2', 'user_id': 5},
]

products = [
    {'id': 1, 'name': 'Товар 1', 'price': 100, 'user_id': 5},
    {'id': 2, 'name': 'Товар 2', 'price': 200, 'user_id': 6},
]


class PostListView(APIView):
    """Список постов (чтение)"""

    @permission_required('post', 'read')
    def get(self, request):
        return Response({
            'success': True,
            'posts': posts
        })


class PostCreateView(APIView):
    """Создание поста"""

    @permission_required('post', 'create')
    def post(self, request):
        new_post = {
            'id': len(posts) + 1,
            'title': request.data.get('title', 'Без названия'),
            'content': request.data.get('content', ''),
            'user_id': request.user.id,
            'status': 'draft'
        }
        posts.append(new_post)
        return Response({
            'success': True,
            'post': new_post
        }, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    """Детали поста"""

    @permission_required('post', 'read')
    def get(self, request, pk):
        post = next((p for p in posts if p['id'] == pk), None)
        if not post:
            return Response({'error': 'Пост не найден'}, status=404)

        # Дополнительная проверка прав для draft статуса
        if post['status'] == 'draft' and post['user_id'] != request.user.id and not request.user.is_staff:
            return Response({'error': 'Доступ запрещен'}, status=403)

        return Response({'success': True, 'post': post})


class PostUpdateView(APIView):
    """Обновление поста"""

    @permission_required('post', 'update')
    def put(self, request, pk):
        post = next((p for p in posts if p['id'] == pk), None)
        if not post:
            return Response({'error': 'Пост не найден'}, status=404)

        # Проверка владельца (owner_only будет проверяться через условия)
        if post['user_id'] != request.user.id and not request.user.is_staff:
            return Response({'error': 'Вы не можете редактировать этот пост'}, status=403)

        post['title'] = request.data.get('title', post['title'])
        post['content'] = request.data.get('content', post['content'])

        return Response({'success': True, 'post': post})


class PostDeleteView(APIView):
    """Удаление поста"""

    @permission_required('post', 'delete')
    def delete(self, request, pk):
        global posts
        post = next((p for p in posts if p['id'] == pk), None)
        if not post:
            return Response({'error': 'Пост не найден'}, status=404)

        # Только админ или владелец
        if post['user_id'] != request.user.id and not request.user.is_staff:
            return Response({'error': 'Доступ запрещен'}, status=403)

        posts = [p for p in posts if p['id'] != pk]
        return Response({'success': True, 'message': 'Пост удален'})


class CommentListView(APIView):
    """Список комментариев"""

    @permission_required('comment', 'read')
    def get(self, request):
        return Response({'success': True, 'comments': comments})


class CommentCreateView(APIView):
    """Создание комментария"""

    @permission_required('comment', 'create')
    def post(self, request):
        new_comment = {
            'id': len(comments) + 1,
            'post_id': request.data.get('post_id'),
            'text': request.data.get('text', ''),
            'user_id': request.user.id
        }
        comments.append(new_comment)
        return Response({'success': True, 'comment': new_comment}, status=201)


class ProductListView(APIView):
    """Список товаров"""

    @permission_required('product', 'read')
    def get(self, request):
        return Response({'success': True, 'products': products})

