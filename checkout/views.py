from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe
from decimal import Decimal
from stripe.error import StripeError


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    current_bag = bag_contents(request)
    total = current_bag['grand_total']

    # Convert to integer cents safely (works when total is Decimal)
    try:
        stripe_total = int(Decimal(total) * Decimal('100'))
    except Exception:
        messages.error(request, "Could not calculate payment total. Please try again.")
        return redirect(reverse('bag'))

    stripe.api_key = stripe_secret_key
    try:
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
    except StripeError:
        messages.error(request, "Payment service error. Please try again later.")
        return redirect(reverse('bag'))

    order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)