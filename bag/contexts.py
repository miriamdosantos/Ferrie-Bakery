from decimal import Decimal, InvalidOperation
from django.conf import settings
from products.models import Product, Flavor

def safe_decimal(value):
    """Converte valores para Decimal com fallback 0.00"""
    try:
        return Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return Decimal('0.00')

def safe_int(value):
    """Converte valores para int com fallback 0"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def bag_contents(request):
    bag = request.session.get('bag', {})
    total = Decimal('0.00')
    bag_items = []

    for item_key, item_data in bag.items():
        product_id = item_data.get('product_id')
        if not product_id:
            continue

        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            continue

        # Flavor
        flavor = None
        flavor_id = item_data.get('flavor_id')
        is_truffled = False
        if flavor_id:
            try:
                flavor = Flavor.objects.get(id=int(flavor_id))
                is_truffled = flavor.is_truffled
            except Flavor.DoesNotExist:
                pass

        # Valores do carrinho
        quantity = safe_int(item_data.get('quantity')) or 1
        quantity_kilo = safe_decimal(item_data.get('quantity_kilo') or 0)
        size = item_data.get('size')
        topper_text = item_data.get('topper_text', '')
        topper_price = safe_decimal(item_data.get('topper_price') or 0)
        roses_quantity = safe_int(item_data.get('roses_quantity') or 0)
        roses_price = safe_decimal(item_data.get('roses_price') or 0)
        roses_price_each = safe_decimal(item_data.get('roses_price_each') or 0)
        message = item_data.get('message', '')
        message_price = safe_decimal(item_data.get('message_price') or 0)
        price = safe_decimal(item_data.get('price') or product.price)

        # Recalcular subtotal
        try:
            base_total = product.calculate_total_price(
                quantity=quantity,
                quantity_kilo=quantity_kilo,
                size=size,
                flavor=flavor,
                topper_text=topper_text,
                roses_quantity=roses_quantity,
                is_truffled=is_truffled
            )
        except Exception:
            base_total = price

        # -------------------------------
        # Subtotal com extras
        # -------------------------------
        subtotal = safe_decimal(base_total) + topper_price + roses_price + message_price
        total += subtotal

        image_url = product.image.url if product.image else None

        bag_items.append({
            'product': product,
            'quantity': quantity,
            'quantity_kilo': quantity_kilo,
            'size': size,
            'price': price,
            'flavor': flavor,
            'is_truffled': is_truffled,
            'topper_text': topper_text,
            'topper_price': topper_price,
            'roses_quantity': roses_quantity,
            'roses_price': roses_price,
            'roses_price_each': roses_price_each,
            'message': message,
            'message_price': message_price,
            'subtotal': subtotal,
            'image': image_url,
            'item_key': item_key,
        })

    # Cálculo do frete
    delivery = Decimal('0.00')
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
    grand_total = total + delivery

    # Contagem segura de produtos (só quantidade, não valor)
    product_count = sum(
        safe_int(item.get('quantity')) + safe_int(item.get('quantity_kilo'))
        for item in bag.values()
    )

    free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total if total < settings.FREE_DELIVERY_THRESHOLD else Decimal('0.00')

    return {
        'bag_items': bag_items,
        'total': total,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
        'product_count': product_count,
    }
