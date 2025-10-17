from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from logbook.models import Trip


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class LocationUpdateAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a Trip associated with the created user (Driver)
        self.trip = Trip.objects.create(
            driver=self.user,
            vehicle_id='T1',
            origin='Start',
            destination='End',
            distance=1.0,
            start_time='2025-10-15T00:00:00Z'
        )

    def test_post_location_update(self):
        url = reverse('trip-location', kwargs={'pk': self.trip.pk}) if 'trip-location' in [u.name for u in []] else f'/api/trips/{self.trip.pk}/location/'
        payload = {
            'lat': 12.34,
            'lng': 56.78,
            'accuracy': 5.5,
            'speed': 10.2,
            'recorded_at': '2025-10-15T12:00:00Z'
        }

        resp = self.client.post(url, data=payload, format='json')
        self.assertIn(resp.status_code, (200, 201), msg=f'Response: {resp.status_code} {resp.content}')
