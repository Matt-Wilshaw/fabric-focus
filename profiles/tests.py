"""Tests for the Profiles app."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from checkout.models import Order, OrderLineItem
from products.models import Category, Product
from profiles.models import UserProfile


class ProfileOrderHistoryTests(TestCase):
    """Regression tests for order-history access control."""

    def setUp(self):
        category = Category.objects.create(
            name='outerwear',
            friendly_name='Outerwear',
        )
        self.product = Product.objects.create(
            category=category,
            sku='PRO-1',
            name='Wool Coat',
            description='A coat for profile tests.',
            price=Decimal('90.00'),
        )
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.owner_profile = UserProfile.objects.get(user=self.owner)
        self.other_profile = UserProfile.objects.get(user=self.other_user)
        self.order = Order.objects.create(
            user_profile=self.owner_profile,
            full_name='Order Owner',
            email='owner@example.com',
            phone_number='07123456789',
            country='GB',
            postcode='SW1A1AA',
            town_or_city='London',
            street_address1='1 Owner Street',
            original_bag='{}',
            stripe_pid='pi_test_profile',
        )
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )

    def test_order_history_requires_login(self):
        response = self.client.get(reverse('order_history', args=[self.order.order_number]))

        expected_login_url = f"{reverse('account_login')}?next=/profile/order_history/{self.order.order_number}"
        self.assertRedirects(response, expected_login_url)

    def test_order_history_blocks_other_authenticated_users(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse('order_history', args=[self.order.order_number]))

        self.assertEqual(response.status_code, 403)

    def test_order_history_allows_order_owner(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('order_history', args=[self.order.order_number]))

        self.assertEqual(response.status_code, 200)
