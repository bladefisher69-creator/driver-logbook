from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock


class RouteViewTest(TestCase):
    @patch('logbook.views_route.requests.post')
    def test_route_success(self, mock_post):
        # Mock a minimal ORS geojson response
        sample = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': {
                        'summary': {'distance': 10000, 'duration': 3600},
                        'segments': [
                            {'steps': [{'instruction': 'Head north', 'distance': 100, 'duration': 60}]}
                        ]
                    },
                    'geometry': {'type': 'LineString', 'coordinates': [[-87.9, 43.0], [-87.6, 41.8]]}
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample
        mock_post.return_value = mock_resp

        url = reverse('api-route')
        resp = self.client.post(url, {'origin': {'lat': 43.0, 'lng': -87.9}, 'destination': {'lat': 41.8, 'lng': -87.6}}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('geometry', data)
        self.assertEqual(data.get('distance_m'), 10000)
