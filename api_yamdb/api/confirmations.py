import os

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_code(user):
    """Отправляет код подтверждения пользователю.
    
    Код выводится в консоль и сохраняется в файл.
    """
    confirmation_code = default_token_generator.make_token(user)

    # Отправляем код через email (сохраняется в mail.outbox).
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        'from@example.com',
        [user.email],
        fail_silently=True,
    )

    # Сохраняем код в файл email/confirmation_codes.txt.
    email_dir = os.path.join(os.path.dirname(__file__), 'email')
    os.makedirs(email_dir, exist_ok=True)
    file_path = os.path.join(email_dir, 'confirmation_codes.txt')
    with open(file_path, 'a') as f:
        f.write(f'User: {user.username}, Email: {user.email}, Code: {confirmation_code}\n')

    return confirmation_code


def check_confirmation_code(user, confirmation_code):
    """Проверяет код подтверждения."""
    return default_token_generator.check_token(user, confirmation_code) 