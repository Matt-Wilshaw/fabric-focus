"""Automated tests for the Products app.

These tests are intentionally small and focus on preventing regressions in
core browsing behaviour (e.g. sorting and filtering).
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class ProductsSortingTests(TestCase):

	"""Tests for server-side sorting of the products list."""

	def setUp(self):
		category = Category.objects.create(
			name='Test Category',
			friendly_name='Test Category',
		)
		Product.objects.create(
			category=category,
			sku='SKU-1',
			name='Alpha',
			description='First',
			price=Decimal('10.00'),
		)
		Product.objects.create(
			category=category,
			sku='SKU-2',
			name='beta',
			description='Second',
			price=Decimal('12.00'),
		)

	def test_sort_by_name_ascending_returns_200(self):
		"""Sorting by name should render the products list successfully."""
		url = reverse('products')
		response = self.client.get(url, {'sort': 'name', 'direction': 'asc'})
		self.assertEqual(response.status_code, 200)
