"""Views for the Home app."""

from django.shortcuts import render


def index(request):
    """Render the home page."""
    return render(request, "home/index.html")
