"""Tests for bag add/update/remove flows."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class BagViewTests(TestCase):
    """Regression coverage for core bag interactions."""

    def setUp(self):
        category = Category.objects.create(
            name='shirts',
            friendly_name='Shirts',
        )
        self.product = Product.objects.create(
            category=category,
            sku='BAG-1',
            name='Oxford Shirt',
            description='A shirt for bag tests.',
            price=Decimal('25.00'),
            has_sizes=True,
        )

    def test_view_bag_loads(self):
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_bag_stores_quantity_in_session(self):
        response = self.client.post(
            reverse('add_to_bag', args=[self.product.id]),
            {
                'quantity': 2,
                'redirect_url': reverse('products'),
            },
        )
        self.assertRedirects(response, reverse('products'))
        self.assertEqual(self.client.session['bag'][str(self.product.id)], 2)

    def test_adjust_bag_updates_quantity(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(
            reverse('adjust_bag', args=[self.product.id]),
            {'quantity': 3},
        )

        self.assertRedirects(response, reverse('view_bag'))
        self.assertEqual(self.client.session['bag'][str(self.product.id)], 3)

    def test_remove_from_bag_returns_200_and_clears_item(self):
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.post(reverse('remove_from_bag', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(str(self.product.id), self.client.session.get('bag', {}))
