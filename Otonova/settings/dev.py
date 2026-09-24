from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8001',
    'http://127.0.0.1:8080',
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8080',
]
