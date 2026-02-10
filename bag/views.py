"""Views for the Bag app."""

from django.shortcuts import render


def view_bag(request):
    """Render the bag contents page."""
    return render(request, "bag/bag.html")
