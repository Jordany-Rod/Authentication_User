# Система разграничения прав доступа (Permission System)

## 1. Общая концепция

Проектируемая система основана на гибридной модели **RBAC (Role-Based Access Control)** с элементами **ABAC (Attribute-Based Access Control)**. Это позволяет гибко управлять доступом как через роли, так и через атрибуты ресурсов.

## 2. Сущности системы

### 2.1. Пользователь (User)
- Существующая модель пользователя
- Может иметь несколько ролей
- Может иметь прямые разрешения (override)

### 2.2. Роль (Role)
Предопределенные наборы прав для групп пользователей.

| Роль | Описание | Типовые права |
|------|----------|---------------|
| admin | Полный доступ ко всем ресурсам | Все действия со всеми ресурсами |
| manager | Управление контентом, но без прав администрирования | CRUD для контента, просмотр пользователей |
| user | Обычный пользователь | Чтение, создание/редактирование только своих объектов |
| guest | Анонимный пользователь | Только чтение публичных ресурсов |

### 2.3. Ресурс (Resource)
Объекты, к которым ограничивается доступ.

| Ресурс | Описание | Примеры |
|--------|----------|---------|
| post | Посты блога | Создание, чтение, редактирование, удаление постов |
| comment | Комментарии | Создание, редактирование, удаление комментариев |
| user_profile | Профили пользователей | Просмотр, редактирование профиля |
| product | Товары (для бизнес-примера) | Просмотр, добавление, редактирование, удаление |

### 2.4. Действие (Action)
Операции, которые можно совершать над ресурсами.

| Действие | Код | Описание |
|----------|-----|----------|
| create | C | Создание нового ресурса |
| read | R | Просмотр ресурса |
| update | U | Обновление ресурса |
| delete | D | Удаление ресурса |
| manage | M | Полное управление (все действия) |

### 2.5. Разрешение (Permission)
Связка "Роль + Ресурс + Действие" с дополнительными условиями.

### 2.6. Условие (Condition)
Дополнительные правила на основе атрибутов (ABAC часть).

Примеры условий:
- `owner_only` - только владелец ресурса
- `status_published` - только опубликованные ресурсы
- `date_range` - ресурсы за определенный период

## 3. Схема базы данных

```sql
-- Роли
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ресурсы
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Действия (CRUD + custom)
CREATE TABLE actions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL, -- 'create', 'read', 'update', 'delete'
    description TEXT
);

-- Разрешения (основа RBAC)
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    action_id INTEGER REFERENCES actions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, resource_id, action_id)
);

-- Пользователи-роли (многие ко многим)
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id),
    UNIQUE(user_id, role_id)
);

-- Прямые разрешения для пользователей (override)
CREATE TABLE user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    action_id INTEGER REFERENCES actions(id) ON DELETE CASCADE,
    is_granted BOOLEAN DEFAULT TRUE, -- TRUE = разрешено, FALSE = запрещено
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, resource_id, action_id)
);

-- Условия для ABAC
CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    condition_type VARCHAR(50) NOT NULL, -- 'owner_only', 'status', 'date_range'
    condition_value JSONB, -- дополнительные параметры в JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Логика проверки доступа

```bash
function check_permission(user, resource, action):
    # 1. Проверка суперпользователя
    if user.is_superuser:
        return GRANTED
    
    # 2. Проверка прямых запретов (blacklist)
    direct_deny = get_user_permission(user, resource, action, is_granted=False)
    if direct_deny:
        return DENIED
    
    # 3. Проверка прямых разрешений
    direct_grant = get_user_permission(user, resource, action, is_granted=True)
    if direct_grant:
        # Проверка дополнительных условий
        if check_conditions(direct_grant, user, resource):
            return GRANTED
    
    # 4. Проверка через роли пользователя
    user_roles = get_user_roles(user)
    for role in user_roles:
        permission = get_permission(role, resource, action)
        if permission and check_conditions(permission, user, resource):
            return GRANTED
    
    return DENIED
```

## 5. Примеры проверки условий

### 5.1. Условие "только владелец"
```bash
def check_owner_condition(user, resource):
    return resource.user_id == user.id
```

### 5.2. Условие "только опубликованные"
```bash
def check_published_condition(resource):
    return resource.status == 'published'
```

### 5.3. Условие "в рабочее время"
```bash
def check_business_hours():
    hour = datetime.now().hour
    return 9 <= hour <= 18
```

## 6. API для управления правами (для администратора)
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET   | /api/admin/roles/| Список ролей|
| POST | /api/admin/roles/ | Создание роли |
| GET | /api/admin/roles/{id}/ | Детали роли |
| PUT | /api/admin/roles/{id}/ | Обновление роли |
| DELETE | /api/admin/roles/{id}/ | Удаление роли |
|  |  |  |
| GET | /api/admin/resources/ | Список ресурсов |
| POST | /api/admin/resources/ | Создание ресурса |
|  |  |  |
| GET | /api/admin/permissions/ | Список разрешений |
| POST | /api/admin/permissions/ | Назначение разрешения роли |
| DELETE | /api/admin/permissions/ | Удаление разрешения |
|       |          |          |
|   POST    |     /api/admin/users/{id}/assign-role/     |     Назначить роль пользователю     |
|   DELETE    |     /api/admin/users/{id}/assign-role/     |     Удалить роль у пользователя     |

## 7. Тестовые данные для демонстрации

```sql
-- Роли
INSERT INTO roles (name, description) VALUES 
('admin', 'Полный доступ ко всем ресурсам'),
('manager', 'Управление контентом'),
('user', 'Обычный пользователь'),
('guest', 'Анонимный пользователь');

-- Ресурсы
INSERT INTO resources (name, description) VALUES 
('post', 'Посты блога'),
('comment', 'Комментарии к постам'),
('user', 'Профили пользователей'),
('product', 'Товары');

-- Действия
INSERT INTO actions (code, description) VALUES 
('create', 'Создание'),
('read', 'Чтение'),
('update', 'Обновление'),
('delete', 'Удаление');

-- Разрешения для роли admin (все на все)
INSERT INTO permissions (role_id, resource_id, action_id) 
SELECT 1, r.id, a.id FROM resources r, actions a;

-- Разрешения для роли manager
INSERT INTO permissions (role_id, resource_id, action_id) VALUES 
(2, 1, 2), -- manager может читать посты
(2, 1, 3), -- manager может обновлять посты
(2, 2, 2), -- manager может читать комментарии
(2, 2, 3); -- manager может обновлять комментарии

-- Разрешения для роли user
INSERT INTO permissions (role_id, resource_id, action_id) VALUES 
(3, 1, 1), -- user может создавать посты
(3, 1, 2), -- user может читать посты
(3, 1, 3), -- user может обновлять свои посты (с условием)
(3, 2, 1), -- user может создавать комментарии
(3, 2, 2); -- user может читать комментарии

-- Назначение ролей пользователям (пример)
INSERT INTO user_roles (user_id, role_id) VALUES 
(1, 1), -- superadmin
(2, 2), -- manager
(3, 3); -- обычный пользователь
```

## 8. Расширяемость 
- Новые ресурсы - просто добавляются в таблицу resources
- Новые действия - добавляются в actions 
- Новые роли - создаются в roles 
- Сложные условия - хранятся в conditions как JSON 
- Прямые разрешения - user_permissions для исключений 
- Запреты - is_granted=False в user_permissions

## 9. Безопасность
 - Проверка доступа происходит на уровне middleware/декораторов 
 - Все запросы к API требуют валидного JWT токена 
 - Прямые запреты имеют приоритет над разрешениями 
 - Условия проверяются на стороне сервера 
 - Логирование всех попыток доступа