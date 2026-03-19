"""Context processor for shopping bag totals and line items."""

from decimal import Decimal
from django.conf import settings
from products.models import Product


def _normalize_quantity(raw_quantity):
    """Return a positive integer quantity or ``None`` when invalid."""
    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return None
    return quantity if quantity > 0 else None

def bag_contents(request):
    """Build bag line items and totals for global template context."""

    # Values exposed to templates (bag page and top-nav total).
    bag_items = []
    total = 0
    product_count = 0

    # Bag is stored in session and keyed by product id.
    # Values can be an int quantity or a size map in `items_by_size`.
    bag = request.session.get('bag', {})
    bag_updated = False

    for item_id, item_data in list(bag.items()):
        # Guard against malformed keys in older or corrupted sessions.
        try:
            normalized_item_id = int(item_id)
        except (TypeError, ValueError):
            bag.pop(item_id, None)
            bag_updated = True
            continue

        # Stale product ids can remain in older sessions; clean them up safely.
        product = Product.objects.filter(pk=normalized_item_id).first()
        if not product:
            bag.pop(item_id, None)
            bag_updated = True
            continue

        # Non-sized products: quantity is stored directly as an integer.
        if isinstance(item_data, int):
            quantity = _normalize_quantity(item_data)
            if quantity is None:
                bag.pop(item_id, None)
                bag_updated = True
                continue

            total += quantity * product.price
            product_count += quantity
            bag_items.append({
                'item_id': item_id,
                'quantity': quantity,
                'product': product,
                'lineitem_total': quantity * product.price,
            })
            
        elif isinstance(item_data, dict) and isinstance(item_data.get('items_by_size'), dict):
            # Size-aware products: quantities are tracked per selected size.
            invalid_size_entries = []
            for size, raw_quantity in item_data['items_by_size'].items():
                quantity = _normalize_quantity(raw_quantity)
                if quantity is None:
                    invalid_size_entries.append(size)
                    continue

                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                    'lineitem_total': quantity * product.price,
                })

            if invalid_size_entries:
                for size in invalid_size_entries:
                    item_data['items_by_size'].pop(size, None)
                bag_updated = True

            if not item_data['items_by_size']:
                bag.pop(item_id, None)
                bag_updated = True
        else:
            bag.pop(item_id, None)
            bag_updated = True

    if bag_updated:
        request.session['bag'] = bag

    # Delivery is free over the configured threshold; otherwise percentage-based.
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    # Final checkout amount shown to the customer.
    grand_total = delivery + total
    
    # Context is injected into templates via Django's context processor mechanism.
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context