from channels.generic.websocket import AsyncWebsocketConsumer

from spotify_to_yt.services import SpotifyToYtService


class SpotifyToYtConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        await SpotifyToYtService.handle_spotify_to_yt(self, text_data)

