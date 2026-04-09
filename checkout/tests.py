"""Tests for checkout entry-point behaviour."""

from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class CheckoutViewTests(TestCase):
    """Focused tests for checkout page access rules."""

    def setUp(self):
        category = Category.objects.create(
            name='essentials',
            friendly_name='Essentials',
        )
        self.product = Product.objects.create(
            category=category,
            sku='CHK-1',
            name='Relaxed Tee',
            description='A tee for checkout tests.',
            price=Decimal('20.00'),
        )

    def test_checkout_redirects_when_bag_is_empty(self):
        response = self.client.get(reverse('checkout'))

        self.assertRedirects(response, reverse('products'))

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_renders_when_bag_has_items(self, mock_create):
        mock_create.return_value.client_secret = 'pi_test_secret_123'

        session = self.client.session
        session['bag'] = {str(self.product.id): 2}
        session.save()

        response = self.client.get(reverse('checkout'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('order_form', response.context)
        self.assertIn('client_secret', response.context)
