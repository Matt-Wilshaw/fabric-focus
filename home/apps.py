"""App configuration for the Home app."""

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Django app configuration for the Home app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        from . import signals  # noqa: F401
