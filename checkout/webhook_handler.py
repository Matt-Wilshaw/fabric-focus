import json
import time
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import HttpResponse

from products.models import Product
from .models import Order, OrderLineItem


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    @staticmethod
    def _event_type(event):
        return event['type'] if isinstance(event, dict) else getattr(event, 'type', 'unknown')

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {self._event_type(event)}',
            status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.retrieve(pid)
        charge = None
        if intent.get('latest_charge'):
            charge = stripe.Charge.retrieve(intent.latest_charge)
        bag = intent.metadata.get('bag', '{}')
        save_info = intent.metadata.get('save_info')
        billing_details = charge.billing_details if charge else {}
        shipping_details = intent.shipping
        amount_pence = charge.amount if charge else intent.amount_received
        grand_total = round(Decimal(amount_pence) / Decimal('100'), 2)

        if not shipping_details:
            shipping_details = {
                'name': '',
                'phone': '',
                'address': {
                    'line1': '',
                    'line2': '',
                    'city': '',
                    'state': '',
                    'postal_code': '',
                    'country': '',
                }
            }

        # Stripe may send empty strings for optional address fields.
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        shipping_name = shipping_details.name or ''
        shipping_phone = shipping_details.phone or ''
        billing_email = (
            getattr(billing_details, 'email', None)
            or intent.get('receipt_email')
            or ''
        )
        country_value = shipping_details.address.country or ''

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_name,
                    email__iexact=billing_email,
                    phone_number__iexact=shipping_phone,
                    country__iexact=country_value,
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
                if attempt <= 5:
                    time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {self._event_type(event)} | VERIFIED order already in database',
                status=200
            )

        try:
            order = Order.objects.create(
                full_name=shipping_name,
                email=billing_email,
                phone_number=shipping_phone,
                country=country_value,
                postcode=shipping_details.address.postal_code,
                town_or_city=shipping_details.address.city,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                county=shipping_details.address.state,
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
            if 'order' in locals():
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {self._event_type(event)} | ERROR: {e}',
                status=500
            )

        return HttpResponse(
            content=f'Webhook received: {self._event_type(event)} | SUCCESS: created order in webhook',
            status=200
        )
    
    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {self._event_type(event)}',
            status=200)
