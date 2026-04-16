"""Tests for checkout entry-point behaviour."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
import stripe

from checkout.models import Order, OrderLineItem
from checkout.webhook_handler import StripeWH_Handler
from profiles.models import UserProfile
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

    def create_order(self, user_profile=None):
        order = Order.objects.create(
            user_profile=user_profile,
            full_name='Test Shopper',
            email='shopper@example.com',
            phone_number='07123456789',
            country='GB',
            postcode='SW1A1AA',
            town_or_city='London',
            street_address1='1 Test Street',
            original_bag='{}',
            stripe_pid='pi_test_checkout',
        )
        OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
        )
        return order

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

    def test_checkout_success_requires_matching_session_for_guest(self):
        order = self.create_order()

        response = self.client.get(reverse('checkout_success', args=[order.order_number]))

        self.assertEqual(response.status_code, 403)

    def test_checkout_success_denies_access_to_other_users_order(self):
        owner = User.objects.create_user(username='owner', password='testpass123')
        intruder = User.objects.create_user(username='intruder', password='testpass123')
        owner_profile = UserProfile.objects.get(user=owner)
        intruder_profile = UserProfile.objects.get(user=intruder)
        order = self.create_order(user_profile=owner_profile)

        self.client.force_login(intruder)
        session = self.client.session
        session['last_order_number'] = order.order_number
        session.save()

        response = self.client.get(reverse('checkout_success', args=[order.order_number]))

        self.assertEqual(response.status_code, 403)
        order.refresh_from_db()
        self.assertEqual(order.user_profile, owner_profile)
        self.assertNotEqual(order.user_profile, intruder_profile)

    def test_checkout_success_allows_order_owner_without_session_match(self):
        owner = User.objects.create_user(username='owner2', password='testpass123')
        owner_profile = UserProfile.objects.get(user=owner)
        order = self.create_order(user_profile=owner_profile)

        self.client.force_login(owner)
        response = self.client.get(reverse('checkout_success', args=[order.order_number]))

        self.assertEqual(response.status_code, 200)

    def test_checkout_success_attaches_guest_order_to_authenticated_user_with_session_match(self):
        user = User.objects.create_user(username='buyer', password='testpass123')
        profile = UserProfile.objects.get(user=user)
        order = self.create_order()

        self.client.force_login(user)
        session = self.client.session
        session['last_order_number'] = order.order_number
        session.save()

        response = self.client.get(reverse('checkout_success', args=[order.order_number]))

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.user_profile, profile)


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


class StripeWebhookHandlerTests(TestCase):
    """Unit tests for webhook handler edge cases."""

    def setUp(self):
        self.handler = StripeWH_Handler(request=None)

    def _event(self, event_type, intent):
        class Event(dict):
            pass

        event = Event(type=event_type)
        event.data = SimpleNamespace(object=intent)
        return event

    @patch('checkout.webhook_handler.Order.objects.get')
    def test_succeeded_event_without_metadata_is_ignored(self, mock_order_get):
        intent = SimpleNamespace(id='pi_test_123', metadata={})
        event = self._event('payment_intent.succeeded', intent)

        response = self.handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Missing checkout metadata', response.content.decode())
        mock_order_get.assert_not_called()

    @patch('checkout.webhook_handler.Order.objects.get')
    def test_succeeded_event_with_metadata_but_missing_shipping_is_ignored(self, mock_order_get):
        intent = SimpleNamespace(
            id='pi_test_456',
            metadata={
                'bag': '{}',
                'save_info': 'false',
                'username': 'AnonymousUser',
            },
            charges=SimpleNamespace(data=[SimpleNamespace(billing_details=None, amount=1000)]),
            shipping=None,
        )
        event = self._event('payment_intent.succeeded', intent)

        response = self.handler.handle_payment_intent_succeeded(event)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Missing billing/shipping details', response.content.decode())
        mock_order_get.assert_not_called()

    @patch('checkout.webhook_handler.send_mail')
    def test_send_confirmation_email_renders_existing_templates(self, mock_send_mail):
        order = Order(
            full_name='Email Tester',
            email='tester@example.com',
            phone_number='07123456789',
            country='GB',
            postcode='SW1A1AA',
            town_or_city='London',
            street_address1='1 Test Street',
            original_bag='{}',
            stripe_pid='pi_test_email',
        )

        self.handler._send_confirmation_email(order)

        mock_send_mail.assert_called_once()
