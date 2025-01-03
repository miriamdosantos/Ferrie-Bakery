from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, Flavor

from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, Flavor

def bag_contents(request):
    bag_items = []
    total = Decimal('0')
    product_count = 0
    bag = request.session.get('bag', {})

    print("Initial bag contents:", bag)  # Debug log

    for item_key, item_data in bag.items():
        try:
            if isinstance(item_data, dict):
                quantity = item_data.get('quantity', 0)
                quantity_kilo = item_data.get('quantity_kilo', 0)
                product_id = item_data.get('product_id') or int(item_key.split('_')[0])
                product = get_object_or_404(Product, pk=product_id)

                size = item_data.get('size')
                flavor_name = item_data.get('flavor')
                flavor = Flavor.objects.filter(name=flavor_name).first() if flavor_name else None
                topper_text = item_data.get('topper_text') if product.has_topper else None
                roses_quantity = item_data.get('roses_quantity', 0) if product.has_roses else 0

                # Calcular o preço base considerando o tamanho
                if product.sale_option == 'size' and size:
                    base_price = product.calculate_price_by_size(size)
                else:
                    base_price = product.price

                total_price = product.calculate_total_price(
                    quantity, quantity_kilo, size=size, flavor=flavor,
                    topper_text=topper_text, roses_quantity=roses_quantity
                )
            else:
                quantity = int(item_data)
                quantity_kilo = 0
                product = get_object_or_404(Product, pk=int(item_key))
                size = None
                flavor = None
                topper_text = None
                roses_quantity = 0
                base_price = product.price
                total_price = product.calculate_total_price(quantity, quantity_kilo)

            total += total_price
            product_count += quantity + (quantity_kilo if product.sale_option == "kilo" else 0)
            
            bag_items.append({
                'item_key': item_key,
                'quantity': quantity,
                'quantity_kilo': quantity_kilo,
                'product': product,
                'size': size,
                'flavor': flavor_name,
                'topper_text': topper_text,
                'roses_quantity': roses_quantity,
                'base_price': base_price,
                'total_price': total_price,
            })

            print(f"Item added: {product.name}, Quantity: {quantity}, Quantity Kilo: {quantity_kilo}, Total: {total_price}")  # Debug log

        except Exception as e:
            print(f"Error processing item {item_key}: {str(e)}")
            continue

    print(f"Subtotal: {total}")  # Debug log

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal('0')
        free_delivery_delta = Decimal('0')

    grand_total = total + delivery

    print(f"Delivery: {delivery}")  # Debug log
    print(f"Grand Total: {grand_total}")  # Debug log

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