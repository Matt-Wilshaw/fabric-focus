from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import json
import stripe
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_email/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_email/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def _get_value(self, obj, key, default=None):
        """Read from either StripeObject-style objects or dictionaries."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _get_payment_intent_charge(self, intent):
        """
        Return the charge for a PaymentIntent.

        Some Stripe API versions include an expanded charges collection on the
        webhook payload; newer payloads commonly provide latest_charge instead.
        """
        charges = self._get_value(intent, 'charges')
        charge_data = self._get_value(charges, 'data', []) if charges else []
        if charge_data:
            return charge_data[0]

        latest_charge = self._get_value(intent, 'latest_charge')
        if latest_charge:
            return stripe.Charge.retrieve(latest_charge)

        return None

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        # Metadata comes from cache_checkout_data before payment confirmation.
        metadata = getattr(intent, 'metadata', {}) or {}

        if hasattr(metadata, 'get'):
            bag = metadata.get('bag')
            save_info = metadata.get('save_info')
            username = metadata.get('username', 'AnonymousUser')
        else:
            bag = getattr(metadata, 'bag', None)
            save_info = getattr(metadata, 'save_info', None)
            username = getattr(metadata, 'username', 'AnonymousUser')

        # Stripe CLI fixtures often omit checkout metadata; acknowledge and skip.
        if not bag:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | INFO: Missing checkout metadata, nothing to reconcile',
                status=200,
            )

        save_info = str(save_info).lower() in ('true', '1', 'yes', 'on')

        charge = self._get_payment_intent_charge(intent)
        billing_details = (
            self._get_value(charge, 'billing_details') if charge else None
        )
        shipping_details = intent.shipping

        if not billing_details or not shipping_details or not shipping_details.address:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | INFO: Missing billing/shipping details, skipped reconciliation',
                status=200,
            )

        grand_total = round(self._get_value(charge, 'amount') / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # If this wasn't an anonymous checkout, attach/update the user's profile.
        profile = None
        if username != 'AnonymousUser':
            user = get_user_model().objects.filter(username=username).first()
            if user:
                profile, _ = UserProfile.objects.get_or_create(user=user)
            if profile and save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        order_exists = False
        attempt = 1
        # Retry briefly to avoid race conditions with the normal checkout view.
        while attempt <= 5:
            try:
                order = Order.objects.get(original_bag=bag, stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                try:
                    order = Order.objects.get(
                        full_name__iexact=shipping_details.name,
                        email__iexact=billing_details.email,
                        phone_number__iexact=shipping_details.phone,
                        country__iexact=shipping_details.address.country,
                        postcode__iexact=shipping_details.address.postal_code,
                        town_or_city__iexact=shipping_details.address.city,
                        street_address1__iexact=shipping_details.address.line1,
                        street_address2__iexact=shipping_details.address.line2,
                        county__iexact=shipping_details.address.state,
                        grand_total=grand_total,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                    order_exists = True
                    break
                except Order.DoesNotExist:
                    attempt += 1
                    time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | SUCCESS: '
                    'Verified order already in database'
                ),
                status=200)
        else:
            order = None
            try:
                # Fallback: create the order from Stripe data + bag metadata.
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(
            content=(
                f'Webhook received: {event["type"]} | SUCCESS: '
                'Created order in webhook'
            ),
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
