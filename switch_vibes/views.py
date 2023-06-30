from django.shortcuts import render
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from django.http import JsonResponse

from .publish import respond_to_mentions

from rest_framework.decorators import APIView


def index(request):
    # respond_to_mentions()
    return HttpResponse("Hello World! Welcome to Switch Vibes! Testing uplaod and deploy.")


class SwitchVibes(APIView):
    def get(self, request, format=None):
        return JsonResponse({"message": "Hello, world!"})


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=respond_to_mentions, trigger="interval", seconds=3)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())
