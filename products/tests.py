"""Automated tests for the Products app."""

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

		def test_category_filter_limits_results(self):
			"""Filtering by category should only return matching products."""
			other_category = Category.objects.create(
				name='Other Category',
				friendly_name='Other Category',
			)
			Product.objects.create(
				category=other_category,
				sku='SKU-3',
				name='Gamma',
				description='Third',
				price=Decimal('14.00'),
			)

			response = self.client.get(reverse('products'), {'category': 'Test Category'})

			self.assertEqual(response.status_code, 200)
			self.assertEqual(len(response.context['products']), 2)

		def test_search_filters_results(self):
			"""Searching should return products matching name/description."""
			response = self.client.get(reverse('products'), {'q': 'First'})

			self.assertEqual(response.status_code, 200)
			self.assertContains(response, 'Alpha')
			self.assertNotContains(response, 'beta')
