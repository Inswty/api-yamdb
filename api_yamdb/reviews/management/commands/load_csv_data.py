import csv
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class Command(BaseCommand):
    """Команда загрузки данных из CSV файлов."""

    help = 'Загружает данные из CSV файлов в базу данных'

    def handle(self, *args, **options):
        """Основной метод импорта данных."""
        self.stdout.write(
            self.style.SUCCESS('Начало загрузки данных из CSV...'))

        # Словарь с моделями и именами файлов.
        models_config = {
            'category.csv': {
                'model': Category,
                'fields': {'name': 'name', 'slug': 'slug'}
            },
            'genre.csv': {
                'model': Genre,
                'fields': {'name': 'name', 'slug': 'slug'}
            },
            'users.csv': {
                'model': User,
                'fields': {
                    'id': 'id',
                    'username': 'username',
                    'email': 'email',
                    'role': 'role',
                    'bio': 'bio',
                    'first_name': 'first_name',
                    'last_name': 'last_name'
                }
            },
            'titles.csv': {
                'model': Title,
                'fields': {
                    'name': 'name',
                    'year': 'year',
                    'description': 'description',
                    'category': 'category'
                }
            },
            'review.csv': {
                'model': Review,
                'fields': {
                    'text': 'text',
                    'score': 'score',
                    'pub_date': 'pub_date',
                    'title_id': 'title',
                    'author': 'author'
                }
            },
            'comments.csv': {
                'model': Comment,
                'fields': {
                    'id': 'id',
                    'text': 'text',
                    'pub_date': 'pub_date',
                    'review_id': 'review',
                    'author': 'author'
                }
            }
        }

        # Проходимся циклом по словарю.
        for filename, config in models_config.items():
            file_path = os.path.join(
                settings.BASE_DIR, 'static', 'data', filename)

            if not os.path.exists(file_path):
                continue

            model = config['model']
            fields_mapping = config['fields']

            # Открываем файл.
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Открываем список объектов которые нужно создать.
                objects_to_create = []

                # Проходимся циклом по строкам файла.
                for row in reader:
                    # Создаем словарь с полями.
                    model_fields = {}

                    # Проходимся по словарю полученному из строк.
                    for csv_field, model_field in fields_mapping.items():
                        if not (csv_field in row and row[csv_field].strip()):
                            continue

                        # Проверяем на категорию и автора,
                        # добавляем их объекты по ключам.
                        if csv_field == 'category':
                            category_id = int(row[csv_field])
                            category = Category.objects.filter(
                                id=category_id
                            ).first()
                            if category:
                                model_fields[model_field] = category
                            continue

                        if csv_field == 'author':
                            author_id = int(row[csv_field])
                            user = User.objects.filter(id=author_id).first()
                            if user:
                                model_fields[model_field] = user
                            continue

                        if csv_field == 'title_id':
                            title_id = int(row[csv_field])
                            title = Title.objects.filter(id=title_id).first()
                            if title:
                                model_fields[model_field] = title
                            continue

                        if csv_field == 'review_id':
                            review_id = int(row[csv_field])
                            review = Review.objects.filter(
                                id=review_id
                            ).first()
                            if review:
                                model_fields[model_field] = review
                            continue

                        # Иначе добавляем в словарь по ключу,
                        # значения из CSV строки.
                        value = row[csv_field].strip()
                        if model_field == 'id':
                            value = int(value)
                        elif model_field == 'year':
                            value = int(value)
                        elif model_field == 'score':
                            value = int(value)
                        elif model_field in ['pub_date']:
                            value = datetime.fromisoformat(
                                value.replace('Z', '+00:00')
                            )
                        model_fields[model_field] = value

                    # Добавляем в созданный список модель с полями.
                    if model_fields:
                        objects_to_create.append(model(**model_fields))

                # Используем bulk_create для создания
                # объектов по созданному списку.
                if objects_to_create:
                    model.objects.bulk_create(
                        objects_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена!'))
