import os
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


ORS_API_KEY = os.getenv('OPENROUTESERVICE_API_KEY', '')


class RouteView(APIView):
    """Proxy route request to OpenRouteService and return simplified geometry and steps.

    Input JSON: { "origin": {"lat":...,"lng":...}, "destination": {...}, "profile": "driving-car" }
    """

    def post(self, request):
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        profile = request.data.get('profile', 'driving-car')

        if not origin or not destination:
            return Response({'detail': 'origin and destination required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build ORS request payload
        coords = [[origin['lng'], origin['lat']], [destination['lng'], destination['lat']]]
        url = f'https://api.openrouteservice.org/v2/directions/{profile}/geojson'
        headers = {'Authorization': ORS_API_KEY, 'Content-Type': 'application/json'}
        payload = {'coordinates': coords, 'instructions': True}

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return Response({'detail': 'Routing provider error', 'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except requests.exceptions.RequestException as e:
            return Response({'detail': 'Routing provider unreachable', 'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        data = r.json()
        features = data.get('features', [])
        if not features:
            return Response({'detail': 'No route returned'}, status=status.HTTP_502_BAD_GATEWAY)

        props = features[0].get('properties', {})
        geometry = features[0].get('geometry')

        # Attempt to extract summary (ORS uses summary in properties.summary)
        summary = props.get('summary', {}) if props else {}
        distance = summary.get('distance', 0)
        duration = summary.get('duration', 0)

        steps = []
        segments = props.get('segments', []) if props else []
        for seg in segments:
            for st in seg.get('steps', []):
                steps.append({
                    'instruction': st.get('instruction'),
                    'distance_m': st.get('distance'),
                    'duration_s': st.get('duration')
                })

        return Response({
            'geometry': geometry,
            'steps': steps,
            'distance_m': distance,
            'duration_s': duration,
            'provider': 'openrouteservice'
        })
