from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings


def dashboard(request):
    user = request.user
    context = {"view": "Dashboard", "user": user}

    return render(request, "dashboard.html", context)


def page404(request):
    user = request.user
    context = {"view": "Dashboard", "user": user}

    return render(request, "404.html", context)
