from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ELDGenerateView(APIView):
    """Stub endpoint for ELD generation. M2 will implement full logic.
    Accepts { driver_id, trip_id } and returns placeholder response for now.
    """

    def post(self, request):
        driver_id = request.data.get('driver_id')
        trip_id = request.data.get('trip_id')

        if not driver_id or not trip_id:
            return Response({'detail': 'driver_id and trip_id required'}, status=status.HTTP_400_BAD_REQUEST)

        # Placeholder response: empty daily_logs list
        return Response({'daily_logs': [], 'svg_urls': [], 'pdf_urls': []})
