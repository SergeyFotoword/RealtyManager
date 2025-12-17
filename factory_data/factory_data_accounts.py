import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diploma.settings')
django.setup()

import factory
from faker import Faker
from django.contrib.auth.hashers import make_password
from django.utils import timezone


from apps.rent.models import (
    User,
    Review,
    Property,
    Listing,
    Address
)