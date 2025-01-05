import difflib
import json

from rest_framework.exceptions import ValidationError


def string_similarity(str1, str2):
    result =  difflib.SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()


def list_similarity(list_1, list_2):
    result = len(set(list_1) & set(list_2)) / float(len(set(list_1) | set(list_2)))
    return result


class Notifier:
    """This class is used for HTTP requests."""
    async def send(self, message: dict):
        if message.get("code") and message.get("code") != 200:
            raise ValidationError(message)


class WebSocketNotifier(Notifier):
    """This class is used for Websocket requests."""
    def __init__(self, consumer):
        self.consumer = consumer

    async def send(self, message):
        await self.consumer.send(text_data=json.dumps(message))
