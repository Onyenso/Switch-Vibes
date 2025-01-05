from channels.generic.websocket import AsyncWebsocketConsumer

from spotify_to_yt.services import SpotifyToYtService
from shared.utils import WebSocketNotifier


class SpotifyToYtConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        notifier = WebSocketNotifier(self)
        await SpotifyToYtService.handle_spotify_to_yt(text_data, notifier)
