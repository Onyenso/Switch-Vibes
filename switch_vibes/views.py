from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello World! Welcome to Switch Vibes! Testing uplaod and deploy.")

