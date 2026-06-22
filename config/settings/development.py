from .base import *  # noqa: F403

DEBUG = env('DJANGO_DEBUG', default=True)  # noqa: F405

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', default='*').split(',')  # noqa: F405

# Additional development specific settings can go here
