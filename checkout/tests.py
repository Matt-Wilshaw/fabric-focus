"""Tests for checkout entry-point behaviour."""

from decimal import Decimal
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
import stripe

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


class WebhookViewTests(TestCase):
    """Coverage for Stripe webhook endpoint behaviour."""

    def setUp(self):
        self.url = reverse('webhook')

    def test_webhook_rejects_get_requests(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    @patch('checkout.webhooks.stripe.Webhook.construct_event')
    def test_webhook_returns_400_on_invalid_payload(self, mock_construct_event):
        mock_construct_event.side_effect = ValueError('Invalid payload')

        response = self.client.post(
            self.url,
            data='not-json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='sig_test',
        )

        self.assertEqual(response.status_code, 400)

    @patch('checkout.webhooks.stripe.Webhook.construct_event')
    def test_webhook_returns_400_on_invalid_signature(self, mock_construct_event):
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            message='Invalid signature',
            sig_header='bad-signature',
        )

        response = self.client.post(
            self.url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='bad-signature',
        )

        self.assertEqual(response.status_code, 400)

    @patch('checkout.webhooks.StripeWH_Handler.handle_payment_intent_succeeded')
    @patch('checkout.webhooks.stripe.Webhook.construct_event')
    def test_webhook_routes_payment_intent_succeeded(self, mock_construct_event, mock_handler):
        event = {'type': 'payment_intent.succeeded'}
        mock_construct_event.return_value = event
        mock_handler.return_value = HttpResponse(status=200)

        response = self.client.post(
            self.url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='sig_test',
        )

        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once_with(event)

    @patch('checkout.webhooks.StripeWH_Handler.handle_event')
    @patch('checkout.webhooks.stripe.Webhook.construct_event')
    def test_webhook_routes_unknown_events_to_generic_handler(self, mock_construct_event, mock_handler):
        event = {'type': 'charge.refunded'}
        mock_construct_event.return_value = event
        mock_handler.return_value = HttpResponse(status=200)

        response = self.client.post(
            self.url,
            data='{}',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='sig_test',
        )

        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once_with(event)
