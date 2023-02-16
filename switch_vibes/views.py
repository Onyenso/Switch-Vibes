from django.shortcuts import render
from django.http import HttpResponse
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from .publish import respond_to_mentions


def index(request):
    respond_to_mentions()
    return HttpResponse("Hello World! Welcome to Switch Vibes! Testing uplaod and deploy.")


scheduler = BackgroundScheduler()
scheduler.add_job(func=respond_to_mentions, trigger="interval", seconds=3)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
