"""Views for the Home app."""

from django.shortcuts import render


def index(request):
    """Render the home page."""
    # Home is a static landing page with no dynamic query logic.
    return render(request, "home/index.html")
