from .base import *

DEBUG = False

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS", "localhost").split(",")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('MYSQL_DATABASE'),
        'USER': env.str('MYSQL_USER'),
        'PASSWORD': env.str('MYSQL_PASSWORD'),
        'HOST': env.str('MYSQL_HOST'),
        'PORT': env.int('MYSQL_PORT'),
    }
}

# Security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False