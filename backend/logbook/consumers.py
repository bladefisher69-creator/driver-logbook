from channels.generic.websocket import AsyncJsonWebsocketConsumer

class TripConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # expecting query param ?trip_id=<id>
        self.trip_id = self.scope['url_route']['kwargs'].get('trip_id')
        self.group_name = f"trip_{self.trip_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        # For now we don't accept client messages, only server broadcasts
        return

    async def location_update(self, event):
        # event contains location payload
        await self.send_json({
            'type': 'location_update',
            'trip_id': event.get('trip_id'),
            'lat': event.get('lat'),
            'lng': event.get('lng'),
            'accuracy': event.get('accuracy'),
            'speed': event.get('speed'),
            'recorded_at': event.get('recorded_at'),
            'arrived': event.get('arrived', False),
        })
