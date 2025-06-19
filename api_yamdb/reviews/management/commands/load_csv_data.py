import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from reviews.models import Category, Genre, Title, Review, Comment
from reviews.constants import MIN_SCORE, MAX_SCORE

User = get_user_model()


class Command(BaseCommand):
    """Команда загрузки данных из CSV файлов."""
    
    help = 'Загружает данные из CSV файлов в базу данных'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропустить существующие записи'
        )
    
    def setup_caches(self):
        """Кэширует все данные из CSV файлов для быстрого доступа."""
        self.stdout.write('Кэширование данных из CSV файлов...')
        
        # Кэши для CSV файлов с основными сущностями (для поиска связей).
        self.caches = {}
        csv_files = ['category.csv', 'titles.csv', 'users.csv', 'review.csv']
        
        for csv_file in csv_files:
            file_path = os.path.join(
                settings.BASE_DIR, 'static', 'data', csv_file
            )
            if not os.path.exists(file_path):
                continue
                
            cache = {}
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    csv_id = int(row['id'])
                    if csv_file == 'category.csv':
                        cache[csv_id] = row['slug'].strip()
                    elif csv_file == 'titles.csv':
                        cache[csv_id] = (
                            row['name'].strip(), int(row['year'])
                        )
                    elif csv_file == 'users.csv':
                        cache[csv_id] = row['username'].strip()
                    elif csv_file == 'review.csv':
                        # Кэшируем логический ключ для отзыва.
                        title_id = int(row['title_id'])
                        author_id = int(row['author'])
                        cache[csv_id] = {
                            'title_id': title_id,
                            'author_id': author_id,
                            'text': row['text'].strip(),
                            'score': int(row['score']),
                            'pub_date': row['pub_date']
                        }
            self.caches[csv_file] = cache
    
    def load_simple_models(self, csv_file, model_class, field_mapping):
        """Универсальный метод для загрузки простых моделей."""
        file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', csv_file
        )
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {csv_file} не найден'))
            return 0
        
        objects = []
        existing_count = 0
        
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                model_data = {
                    model_field: row[csv_field].strip()
                    for csv_field, model_field in field_mapping.items()
                    if csv_field in row and row[csv_field].strip()
                }
                
                if not model_data:
                    continue
                
                # Проверяем существование записи по уникальным полям.
                if model_class == Category or model_class == Genre:
                    # Для категорий и жанров проверяем по slug.
                    if model_class.objects.filter(
                        slug=model_data.get('slug')
                    ).exists():
                        existing_count += 1
                        continue
                elif model_class == User:
                    # Для пользователей проверяем по username и email.
                    if model_class.objects.filter(
                        username=model_data.get('username'),
                        email=model_data.get('email')
                    ).exists():
                        existing_count += 1
                        continue
                
                objects.append(model_class(**model_data))
        
        if objects:
            created_objects = model_class.objects.bulk_create(
                objects, ignore_conflicts=True
            )
            created = len(created_objects)
            message = (
                f'{model_class.__name__}: создано {created}, '
                f'пропущено {existing_count} записей'
            )
            self.stdout.write(self.style.SUCCESS(message))
            return created
        return 0
    
    def load_titles(self):
        """Загружает произведения с использованием кэша категорий."""
        file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', 'titles.csv'
        )
        objects = []
        existing_count = 0
        
        # Создаем карту slug -> Category.
        category_map = {cat.slug: cat for cat in Category.objects.all()}
        
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name'].strip()
                year = int(row['year'])
                
                # Проверяем существование произведения.
                if Title.objects.filter(name=name, year=year).exists():
                    existing_count += 1
                    continue
                
                # Получаем категорию через кэш.
                category = None
                if row.get('category'):
                    category_csv_id = int(row['category'])
                    category_slug = self.caches.get('category.csv', {}).get(
                        category_csv_id
                    )
                    if category_slug:
                        category = category_map.get(category_slug)
                
                objects.append(Title(
                    name=name,
                    year=year,
                    category=category,
                    description=''
                ))
        
        if objects:
            created_objects = Title.objects.bulk_create(
                objects, ignore_conflicts=True
            )
            created = len(created_objects)
            message = (
                f'Title: создано {created}, пропущено {existing_count}'
            )
            self.stdout.write(self.style.SUCCESS(message))
            return created
        return 0
    
    def load_genre_title_relations(self):
        """Загружает связи жанр-произведение."""
        file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', 'genre_title.csv'
        )
        created = 0
        existing_count = 0
        
        # Создаем карты для быстрого поиска.
        title_map = {title.id: title for title in Title.objects.all()}
        genre_map = {genre.id: genre for genre in Genre.objects.all()}
        
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title_id = int(row['title_id'])
                genre_id = int(row['genre_id'])
                
                title = title_map.get(title_id)
                genre = genre_map.get(genre_id)
                
                if not (title and genre):
                    continue
                
                # Проверяем существование связи.
                if title.genre.filter(id=genre.id).exists():
                    existing_count += 1
                    continue
                
                title.genre.add(genre)
                created += 1
        
        message = (
            f'Genre-Title: создано {created}, пропущено {existing_count}'
        )
        self.stdout.write(self.style.SUCCESS(message))
        return created
    
    def load_reviews_and_comments(self):
        """Универсальный метод для загрузки отзывов и комментариев."""
        # Создаем карты для быстрого поиска.
        title_map = {
            (title.name, title.year): title 
            for title in Title.objects.all()
        }
        user_map = {user.username: user for user in User.objects.all()}
        
        # Загружаем отзывы
        reviews_created = self._load_reviews(title_map, user_map)
        
        # Загружаем комментарии
        comments_created = self._load_comments(title_map, user_map)
        
        return reviews_created + comments_created
    
    def _load_reviews(self, title_map, user_map):
        """Загружает отзывы."""
        file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', 'review.csv'
        )
        objects = []
        existing_count = 0
        skipped_count = 0
        
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                review_data = self.caches.get(
                    'review.csv', {}).get(int(row['id']))
                if not review_data:
                    skipped_count += 1
                    continue
                
                # Получаем связанные объекты через кэши.
                title_info = self.caches.get('titles.csv', {}).get(
                    review_data['title_id']
                )
                username = self.caches.get('users.csv', {}).get(
                    review_data['author_id']
                )
                
                if not (title_info and username):
                    skipped_count += 1
                    continue
                
                title = title_map.get(title_info)
                author = user_map.get(username)
                
                if not (title and author and (
                    MIN_SCORE <= review_data['score'] <= MAX_SCORE)
                ):
                    skipped_count += 1
                    continue
                
                # Проверяем существование отзыва
                # (уникальное ограничение author+title).
                if Review.objects.filter(
                    author=author, title=title
                ).exists():
                    existing_count += 1
                    continue
                
                pub_date = datetime.fromisoformat(
                    review_data['pub_date'].replace('Z', '+00:00')
                )
                
                objects.append(Review(
                    title=title,
                    text=review_data['text'],
                    author=author,
                    score=review_data['score'],
                    pub_date=pub_date
                ))
        
        if objects:
            created_objects = Review.objects.bulk_create(
                objects, ignore_conflicts=True
            )
            created = len(created_objects)
            message = (
                f'Review: создано {created}, пропущено {existing_count}, '
                f'невалидных {skipped_count} записей'
            )
            self.stdout.write(self.style.SUCCESS(message))
            return created
        return 0
    
    def _load_comments(self, title_map, user_map):
        """Загружает комментарии."""
        file_path = os.path.join(
            settings.BASE_DIR, 'static', 'data', 'comments.csv'
        )
        objects = []
        existing_count = 0
        skipped_count = 0
        
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                review_csv_id = int(row['review_id'])
                author_csv_id = int(row['author'])
                
                # Получаем данные отзыва через кэш
                review_data = self.caches.get(
                    'review.csv', {}).get(review_csv_id)
                username = self.caches.get(
                    'users.csv', {}).get(author_csv_id)
                
                if not (review_data and username):
                    skipped_count += 1
                    continue
                
                # Получаем данные произведения и автора отзыва.
                title_info = self.caches.get(
                    'titles.csv', {}).get(review_data['title_id'])
                review_author_username = self.caches.get(
                    'users.csv', {}).get(review_data['author_id'])
                
                if not (title_info and review_author_username):
                    skipped_count += 1
                    continue
                
                title_name, title_year = title_info
                author = user_map.get(username)
                
                if not author:
                    skipped_count += 1
                    continue
                
                # Ищем отзыв в БД по логическому ключу используя Django ORM.
                review = Review.objects.filter(
                    title__name=title_name,
                    title__year=title_year,
                    author__username=review_author_username
                ).first()
                
                if not review:
                    skipped_count += 1
                    continue
                
                # Проверяем существование комментария.
                if Comment.objects.filter(
                    review=review, 
                    author=author, 
                    text=row['text'].strip()
                ).exists():
                    existing_count += 1
                    continue
                
                pub_date = datetime.fromisoformat(
                    row['pub_date'].replace('Z', '+00:00')
                )
                
                objects.append(Comment(
                    review=review,
                    text=row['text'].strip(),
                    author=author,
                    pub_date=pub_date
                ))
        
        if objects:
            created_objects = Comment.objects.bulk_create(
                objects, ignore_conflicts=True
            )
            created = len(created_objects)
            message = (
                f'Comment: создано {created}, пропущено {existing_count}, '
                f'невалидных {skipped_count} записей'
            )
            self.stdout.write(self.style.SUCCESS(message))
            return created
        return 0
    
    def handle(self, *args, **options):
        """Основной метод выполнения команды."""
        self.stdout.write(self.style.SUCCESS(
            'Начало финальной оптимизированной загрузки...'))
        
        # Кэшируем все данные.
        self.setup_caches()
        
        total_created = 0
        
        # Загружаем данные в правильном порядке.
        total_created += self.load_simple_models(
            'category.csv', Category, {'name': 'name', 'slug': 'slug'}
        )
        
        total_created += self.load_simple_models(
            'genre.csv', Genre, {'name': 'name', 'slug': 'slug'}
        )
        
        total_created += self.load_simple_models(
            'users.csv', User, {
                'username': 'username',
                'email': 'email',
                'role': 'role',
                'bio': 'bio',
                'first_name': 'first_name',
                'last_name': 'last_name'
            }
        )
        
        total_created += self.load_titles()
        total_created += self.load_genre_title_relations()
        total_created += self.load_reviews_and_comments()
        
        message = (
            f'Финальная загрузка завершена! Всего создано: {total_created}'
        )
        self.stdout.write(self.style.SUCCESS(message)) 