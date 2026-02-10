"""Views for the Bag app."""

from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404

from products.models import Product


def view_bag(request):
    """Render the bag contents page."""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the session-backed bag."""

    product = get_object_or_404(Product, pk=item_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    redirect_url = request.POST.get('redirect_url') or reverse('view_bag')

    bag = request.session.get('bag', {})
    item_id_str = str(item_id)
    bag[item_id_str] = bag.get(item_id_str, 0) + quantity
    request.session['bag'] = bag

    messages.success(request, f'Added {product.name} to your bag')
    return redirect(redirect_url)
