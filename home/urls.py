"""URL routes for the Home app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('style-assistant/', views.style_assistant, name='style_assistant'),
]
