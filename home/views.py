from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    """Return the index page for the home app."""
    # If the template is missing, return a simple response so app imports cleanly.
    try:
        return render(request, "home/index.html")
    except Exception:
        return HttpResponse("Home index")