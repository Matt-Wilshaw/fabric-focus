"""Admin configuration for the Products app.

Defines how Product and Category appear in the Django admin interface.
"""

from django.contrib import admin

from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    """Admin list view configuration for products."""
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)

class CategoryAdmin(admin.ModelAdmin):
    """Admin list view configuration for categories."""
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)