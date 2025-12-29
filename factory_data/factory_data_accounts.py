import uuid
import factory
from faker import Faker
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from apps.accounts.models.role import Role
from apps.accounts.models.profile import UserProfile

faker = Faker()
User = get_user_model()

ROLE_TENANT_NAME = "TENANT"
ROLE_LANDLORD_NAME = "LANDLORD"


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    # IMPORTANT: must match other seeders' pickers
    name = factory.Iterator([ROLE_TENANT_NAME, ROLE_LANDLORD_NAME])


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:12]}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.LazyAttribute(lambda _: f"+{faker.msisdn()[:12]}")

    is_active = True
    is_staff = False
    date_joined = factory.LazyFunction(timezone.now)

    # deterministic password for seeded users
    password = factory.LazyFunction(lambda: make_password("password123"))


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)

    nickname = factory.LazyFunction(lambda: f"user_{uuid.uuid4().hex[:10]}")

    avatar = None
    bio = factory.Faker("sentence", nb_words=12)

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.user.roles.set(extracted)


def run(
    users_count: int = 480,
    staff_count: int = 20,
) -> None:
    print("Creating roles…")
    tenant_role, _ = Role.objects.get_or_create(name="TENANT")
    landlord_role, _ = Role.objects.get_or_create(name="LANDLORD")

    print("Creating 480 regular users…")
    for i in range(users_count):
        role = tenant_role if i % 2 == 0 else landlord_role

        profile = UserProfileFactory()
        profile.user.roles.add(role)

    print("Creating 20 staff users…")
    for i in range(staff_count):
        role = tenant_role if i % 2 == 0 else landlord_role

        profile = UserProfileFactory(user__is_staff=True)
        profile.user.roles.add(role)

    print("Accounts seeded successfully")
