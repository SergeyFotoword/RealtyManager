from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

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