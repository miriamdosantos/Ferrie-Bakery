from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, Flavor

from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, Flavor

def bag_contents(request):
    """Calcula os itens do carrinho e o total."""
    bag_items = []
    total = Decimal('0')
    product_count = 0
    bag = request.session.get('bag', {})

    for item_key, item_data in bag.items():
        try:
            if isinstance(item_data, dict):
                quantity = item_data.get('quantity', 0)
                quantity_kilo = item_data.get('quantity_kilo', 0)
                product_id = item_data.get('product_id') or int(item_key.split('_')[0])
                product = get_object_or_404(Product, pk=product_id)
                price = product.price

                size = item_data.get('size')
                flavor_name = item_data.get('flavor')
                flavor = Flavor.objects.filter(name=flavor_name).first() if flavor_name else None

                total_price = product.calculate_total_price(
                    quantity, quantity_kilo, size=size, flavor=flavor
                )

                total += total_price
                product_count += quantity + (quantity_kilo if product.sale_option == "kilo" else 0)

                bag_items.append({
                    'item_key': item_key,
                    'quantity': quantity,
                    'quantity_kilo': quantity_kilo,
                    'price': price,
                    'product': product,
                    'size': size,
                    'flavor': flavor_name,
                    'total_price': total_price,
                })

        except Exception as e:
            print(f"Error processing item {item_key}: {str(e)}")
            continue

    # Calcula o custo do frete, caso necessário
    delivery = Decimal('0')
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
    grand_total = total + delivery

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': settings.FREE_DELIVERY_THRESHOLD - total if total < settings.FREE_DELIVERY_THRESHOLD else 0,
        'grand_total': grand_total,
    }

    return context