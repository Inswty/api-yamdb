from reviews.validators import validate_username_format


class UsernameValidationMixin:
    """Миксин для валидации username."""

    def validate_username(self, username):
        return validate_username_format(username)
