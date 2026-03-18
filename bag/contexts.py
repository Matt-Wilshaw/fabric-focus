"""Context processor for shopping bag totals and line items."""

from decimal import Decimal
from django.conf import settings
from products.models import Product

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

        # Stale product ids can remain in older sessions; clean them up safely.
        product = Product.objects.filter(pk=item_id).first()
        if not product:
            bag.pop(item_id, None)
            bag_updated = True
            continue

        # Non-sized products: quantity is stored directly as an integer.
        if isinstance(item_data, int):
            total += item_data * product.price
            product_count += item_data
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
                'lineitem_total': item_data * product.price,
            })
            
        elif isinstance(item_data, dict) and isinstance(item_data.get('items_by_size'), dict):
            # Size-aware products: quantities are tracked per selected size.
            for size, quantity in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                    'lineitem_total': quantity * product.price,
                })
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