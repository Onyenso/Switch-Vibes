from channels.generic.websocket import AsyncWebsocketConsumer

from switch_vibes.services import YtToSpotifyService


class YtToSpotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        await YtToSpotifyService.handle_yt_to_spotify(self, text_data)
