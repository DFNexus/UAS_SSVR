from .base import *  # noqa: F403

# Override DATABASES to use SQLite in-memory for very fast testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Override password hashers to use a fast, insecure algorithm during testing
# This significantly speeds up test execution when creating User objects
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
