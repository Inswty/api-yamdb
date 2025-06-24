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

        models_config = {
            'category.csv': Category,
            'genre.csv': Genre,
            'users.csv': User,
            'titles.csv': Title,
            'review.csv': Review,
            'comments.csv': Comment
        }

        for filename, model in models_config.items():
            file_path = os.path.join(
                settings.BASE_DIR, 'static', 'data', filename)

            if not os.path.exists(file_path):
                continue

            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                objects_to_create = []

                for row in reader:
                    model_fields = {}

                    for field, value in row.items():
                        if not value.strip():
                            continue

                        if field == 'category':
                            category = Category.objects.filter(
                                id=int(value)).first()
                            if category:
                                model_fields[field] = category
                        elif field == 'author':
                            user = User.objects.filter(id=int(value)).first()
                            if user:
                                model_fields[field] = user
                        else:
                            model_fields[field] = value.strip()

                    if model_fields:
                        objects_to_create.append(model(**model_fields))

                if objects_to_create:
                    model.objects.bulk_create(
                        objects_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Загрузка данных завершена!'))
