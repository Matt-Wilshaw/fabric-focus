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

    def test_profile_order_history_displays_saved_lineitem_size(self):
        """Profile history should render line-item product_size values."""
        sized_product = Product.objects.create(
            category=self.product.category,
            sku='PRO-2',
            name='Sized Hoodie',
            description='Sized item for profile display test.',
            price=Decimal('55.00'),
            has_sizes=True,
        )
        OrderLineItem.objects.create(
            order=self.order,
            product=sized_product,
            product_size='m',
            quantity=1,
        )

        self.client.force_login(self.owner)
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Size M')


class UserProfileSignalTests(TestCase):
    """Tests for user/profile signal resilience."""

    def test_saving_user_without_profile_recreates_profile(self):
        user = User.objects.create_user(username='legacy-user', password='testpass123')
        UserProfile.objects.filter(user=user).delete()

        user.first_name = 'Legacy'
        user.save()

        self.assertTrue(UserProfile.objects.filter(user=user).exists())
