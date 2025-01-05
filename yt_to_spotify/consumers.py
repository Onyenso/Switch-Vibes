from channels.generic.websocket import AsyncWebsocketConsumer

from yt_to_spotify.services import YtToSpotifyService
from shared.utils import WebSocketNotifier


class YtToSpotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        notifier = WebSocketNotifier(self)
        await YtToSpotifyService.handle_yt_to_spotify(text_data, notifier)
