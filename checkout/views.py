from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm

def checkout(request):
    # Retrieve shopping bag from session
    bag = request.session.get('bag', {})
    # If bag is empty, show error and redirect to products page
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))
    
    # Initialize empty order form
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    # Prepare context for template rendering
    context = {
        'order_form': order_form,
    }

    # Render checkout page with order form
    return render(request, template, context)