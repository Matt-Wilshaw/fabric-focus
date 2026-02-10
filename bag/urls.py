"""URL routes for the Bag app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='view_bag')
]
