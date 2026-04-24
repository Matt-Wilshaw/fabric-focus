"""Database models for the Products app.

These models represent the catalogue structure (categories and products)
displayed in the shopfront.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    """A product category used for filtering and navigation."""

    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        """Return the category name as the human-readable representation."""
        return self.name

    def get_friendly_name(self):
        """Return a user-friendly display name, if provided."""
        return self.friendly_name


class Product(models.Model):
    """A product in the catalogue."""
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        """Return the product name as the human-readable representation."""
        return self.name
