"""App configuration for the Products app."""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Django app configuration for the Products app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
