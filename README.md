# User Portal - cистема аутентификации и авторизации

## Описание проекта

Backend-приложение для управления пользователями и разграничения прав доступа.
Реализована собственная система аутентификации и авторизации.

### Основные возможности

- Регистрация, вход и выход пользователей
- Управление профилем (просмотр, обновление, мягкое удаление)
- Смена пароля
- JWT аутентификация
- Система ролей и прав доступа (RBAC + ABAC)
- Управление правами через админ-панель
- Демо-объекты для проверки прав (посты, комментарии, товары)

## Технологии

- **Python** 3.8+
- **Django** 4.2+
- **Django REST Framework** 3.15+
- **PyJWT** - для работы с токенами
- **SQLite**

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Jordany-Rod/Authentication_User.git
cd User_Portal
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для Linux/Mac:
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных
```bash
python manage.py migrate
```

### 5. Создание суперпользователя
```bash
python manage.py runserver
```
Сервер будет доступен по адресу: http://127.0.0.1:8000/

## Документация API

### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /api/auth/register/ | Регистрация нового пользователя |
|   POST    |     /api/auth/login/     |     Вход в систему     |
|   POST    |    /api/auth/logout/      |     Выход (добавление токена в черный список)     |
|   POST    |     /api/auth/refresh/     |     Обновление access токена     |
|    POST   |     /api/auth/change-password/     |     Смена пароля     |
|   DELETE    |     /api/auth/delete-account/     |       Мягкое удаление аккаунта   |

### Профиль пользователя

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
|   GET    |     /api/auth/profile/     |      Получение данных профиля    |
|   PUT    |     /api/auth/profile/     |     Обновление профиля     |
|    GET   |     /api/auth/me/     |     Информация о текущем пользователе     |

### Управление правами (только для администраторов)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
|   CRUD    |     /api/auth/admin/roles/     |     Управление ролями     |
|    CRUD   |    /api/auth/admin/resources/      |     Управление ресурсами     |
|    CRUD   |     /api/auth/admin/actions/     |     Управление действиями     |
|    CRUD   |     /api/auth/admin/permissions/     |     Управление разрешениями     |
|   CRUD    |     /api/auth/admin/user-roles/     |       Назначение ролей пользователям   |
|   GET    |     /api/auth/admin/users/     |     Просмотр пользователей     |

### Демо-объекты (бизнес-логика)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
|   CRUD    |     /api/business/posts/     |     Управление постами     |
|   CRUD    |     /api/business/comments/     |     Управление комментариями     |
|   CRUD    |     /api/business/products/     |     Управление товарами     |
|    CRUD   |     /api/business/orders/     |      Управление заказами    |
|   CRUD    |     /api/business/categories/     |     Управление категориями     |

## Система прав доступа

Подробное описание системы прав находится в файле PERMISSIONS.md

### Основные принципы
1. RBAC (Role-Based Access Control) - доступ через роли
2. ABAC (Attribute-Based Access Control) - условия на атрибутах
3. Прямые разрешения - override для конкретных пользователей
4. Приоритет запретов - запрет имеет больший приоритет

### Тестирование

## Тестовые пользователи

| Email | Пароль | Роль |
|-------|--------|------|
|   admin@example.com    |    testpass123    |   Администратор   |
|   manager@example.com    |     testpass123   |   Менеджер   |
|   user1@example.com    |    testpass123    |   Обычный пользователь   |
|   seller1@example.com    |    testpass123    |   Продавец   |

## Заполнение тестовыми данными

```bash
# Полная очистка и заполнение
python manage.py seed_all --clear

# Только права
python manage.py seed_permissions

# Только бизнес-объекты
python manage.py seed_business
```
## Контакты

Разработчик: Егор Родионов

Email: erop1997@mail.ru

---

Проект разработан в рамках тестового задания

