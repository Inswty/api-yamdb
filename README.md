YaMDb - это API для сбора отзывов пользователей на различные произведения (фильмы, книги, музыку).

Проект состоит из:
Приложения reviews - основная бизнес-логика
Приложения api - интерфейс взаимодействия через API

Установка и запуск:
Клонировать репозиторий
Установить зависимости: 
```
pip install -r requirements.txt
```
Применить миграции:
```
python manage.py migrate
```
Запустить сервер:
```
python manage.py runserver
```
Наполнение базы данных:
Для загрузки тестовых данных из CSV-файлов выполнить:
(bash)
```
python manage.py load_csv_data
```
API Endpoints:
Аутентификация
POST /api/v1/auth/signup/ - Регистрация нового пользовател
POST /api/v1/auth/token/ - Получение JWT-токена

Пользователи
GET /api/v1/users/ - Список всех пользователей (admin only)
POST /api/v1/users/ - Создание пользователя (admin only)
GET /api/v1/users/{username}/ - Получение пользователя (admin only)
PATCH /api/v1/users/{username}/ - Изменение пользователя (admin only)
DELETE /api/v1/users/{username}/ - Удаление пользователя (admin only)
GET /api/v1/users/me/ - Получение своего профиля
PATCH /api/v1/users/me/ - Изменение своего профиля

Произведения (Titles)
GET /api/v1/titles/ - Список произведений
POST /api/v1/titles/ - Создание произведения (admin only)
GET /api/v1/titles/{titles_id}/ - Получение произведения
PATCH /api/v1/titles/{titles_id}/ - Изменение произведения (admin only)
DELETE /api/v1/titles/{titles_id}/ - Удаление произведения (admin only)

Категории (Categories)
GET /api/v1/categories/ - Список категорий
POST /api/v1/categories/ - Создание категории (admin only)
DELETE /api/v1/categories/{slug}/ - Удаление категории (admin only)

Жанры (Genres)
GET /api/v1/genres/ - Список жанров
POST /api/v1/genres/ - Создание жанра (admin only)
DELETE /api/v1/genres/{slug}/ - Удаление жанра (admin only)

Отзывы (Reviews)
GET /api/v1/titles/{title_id}/reviews/ - Список отзывов
POST /api/v1/titles/{title_id}/reviews/ - Создание отзыва
GET /api/v1/titles/{title_id}/reviews/{review_id}/ - Получение отзыва
PATCH /api/v1/titles/{title_id}/reviews/{review_id}/ - Изменение отзыва
DELETE /api/v1/titles/{title_id}/reviews/{review_id}/ - Удаление отзыва

Комментарии (Comments)
GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Список комментариев
POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Создание комментария
GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - Получение комментария
PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - Изменение комментария
DELETE /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - Удаление комментария

Пользовательские роли и права:
Аноним: только чтение
Аутентифицированный пользователь (user): чтение, создание отзывов/комментариев, изменение/удаление своих отзывов/комментариев
Модератор (moderator): все права user + возможность изменять/удалять любые отзывы и комментарии
Администратор (admin): полные права на управление контентом и пользователями

Тестирование
Запуск тестов:
```
pytest -v
```

Технологический стек:
Python 3.12.7
Django 5.1.1
Django REST Framework 5.4.0
Simple JWT (JWT-аутентификация)
SQLite
Swagger/ReDoc (документация API)

Авторы:
Проект разработан [Павел Куличенко, Евгений Актемиров]
GitHub: https://github.com/Inswty