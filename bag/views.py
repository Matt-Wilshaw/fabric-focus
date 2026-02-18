"""Views for the Bag app.

These views handle the basket page and session-backed add-to-bag behaviour,
including optional product sizes.
"""

from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

def view_bag(request):
    """Render the bag contents page."""

    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the session bag.

    If a size is posted, quantities are tracked per size under
    `items_by_size`; otherwise, quantity is stored directly by item id.
    """

    item_id = str(item_id)

    # Quantity selector from the product form.
    quantity = int(request.POST.get('quantity'))
    # URL we return to after adding the item.
    redirect_url = request.POST.get('redirect_url')

    # Optional size selection (e.g. XS/S/M/L/XL).
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    # Bag is persisted in the session as a dictionary.
    bag = request.session.get('bag', {})

    if size:
        # Size-aware items are nested by `items_by_size`.
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    else:
        # Non-sized items are tracked as a single quantity value.
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

    # Persist updated bag structure back to the user's session.
    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """Adjust the quantity of a product in the session bag."""

    item_id = str(item_id)
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product_size')
    bag = request.session.get('bag', {})

    if size:
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
        else:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
    else:
        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """Remove a product (or specific size) from the session bag."""

    try:
        item_id = str(item_id)
        size = request.POST.get('product_size') or request.POST.get('size')
        bag = request.session.get('bag', {})

        if size:
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
        else:
            bag.pop(item_id)

        request.session['bag'] = bag
        return HttpResponse(status=200)
    except Exception:
        return HttpResponse(status=500)