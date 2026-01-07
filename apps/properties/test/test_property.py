from django.test import TestCase
from apps.properties.models import Amenity

class AmenityModelTest(TestCase):
    def test_slug_is_generated(self):
        amenity = Amenity.objects.create(name="Wi Fi")
        self.assertEqual(amenity.slug, "wi-fi")

    def test_only_active_returned(self):
        Amenity.objects.create(name="Active", is_active=True)
        Amenity.objects.create(name="Inactive", is_active=False)

        qs = Amenity.objects.filter(is_active=True)
        self.assertEqual(qs.count(), 1)