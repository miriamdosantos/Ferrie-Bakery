from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product, Flavor
from decimal import Decimal
import uuid
from products.models import Flavor


from django.http import JsonResponse


def view_bag(request):
    """Display the shopping bag with correct calculations."""
    
    bag = request.session.get("bag", {})
    bag_items = []
    total = Decimal("0.00")
    delivery = Decimal("0.00")  # Adjust if needed

    for item_key, item_data in bag.items():
        product = get_object_or_404(Product, pk=item_data["product_id"])

        # Flavor
        flavor = None
        if item_data.get("flavor_id"):
            try:
                flavor = Flavor.objects.get(pk=item_data["flavor_id"])
            except Flavor.DoesNotExist:
                flavor = None

        # Quantities
        quantity = int(item_data.get("quantity", 0)) if item_data.get("quantity") else 0
        quantity_kilo = Decimal(item_data.get("quantity_kilo", 0)) if item_data.get("quantity_kilo") else Decimal("0.00")

        # Extras
        topper_price = Decimal(item_data.get("topper_price", "0"))
        roses_price = Decimal(item_data.get("roses_price", "0"))
        roses_price_each = Decimal(item_data.get("roses_price_each", "0"))
        message_price = Decimal(item_data.get("message_price", "0"))

        # Base and full unit price
        base_price = Decimal(item_data.get("price", product.price))
        full_unit_price = base_price + topper_price + roses_price + message_price

        # Subtotal calculation
        if quantity and quantity_kilo:
            subtotal = full_unit_price * quantity * quantity_kilo
        elif quantity_kilo:
            subtotal = full_unit_price * quantity_kilo
        elif quantity:
            subtotal = full_unit_price * quantity
        else:
            subtotal = full_unit_price

        total += subtotal

        # Prepare for template
        bag_items.append({
            "item_key": item_key,
            "product": product,
            "flavor": flavor,
            "quantity": quantity,
            "quantity_kilo": quantity_kilo,
            "size": item_data.get("size"),
            "topper_text": item_data.get("topper_text", ""),
            "topper_price": topper_price,
            "roses_quantity": int(item_data.get("roses_quantity", 0)),
            "roses_price_each": roses_price_each,
            "roses_price": roses_price,
            "message": item_data.get("message", ""),
            "message_price": message_price,
            "unit_price": full_unit_price,  # single unit with extras
            "subtotal": subtotal,
        })

    # Delivery & totals
    free_delivery_delta = max(Decimal("0.00"), Decimal("50.00") - total)
    grand_total = total + delivery

    context = {
        "bag_items": bag_items,
        "total": total,
        "delivery": delivery,
        "grand_total": grand_total,
        "free_delivery_delta": free_delivery_delta,
    }

    return render(request, "bag/bag.html", context)

# bag/views.py
from decimal import Decimal

def add_to_bag(request, item_id):
    product = get_object_or_404(Product, pk=item_id)
    bag = request.session.get("bag", {})

    quantity = int(request.POST.get("quantity", 1))
    quantity_kilo = Decimal(request.POST.get("quantity_kilo") or "0")
    size = request.POST.get("size")
    flavor_id = request.POST.get("flavor")
    flavor = get_object_or_404(Flavor, pk=flavor_id) if flavor_id else None
    topper_text = request.POST.get("topper_text")
    roses_quantity = int(request.POST.get("roses_quantity", 0))
    message = request.POST.get("message")

    item_key = str(uuid.uuid4())[:8]

    # CALCULA O TOTAL USANDO O MÉTODO DO PRODUCT
    subtotal = product.calculate_total_price(
        quantity=quantity,
        quantity_kilo=quantity_kilo,
        size=size,
        flavor=flavor,
        topper_text=topper_text,
        roses_quantity=roses_quantity,
    )

    # Extras individuais
    topper_price = product.get_topper_price() if topper_text else Decimal("0.0")
    roses_price_each = product.get_roses_price(roses_quantity, return_individual=True)
    roses_price = product.get_roses_price(roses_quantity, return_individual=False)
    message_price = Decimal("0.0")  # Ajuste se houver price real

    # unit_price = subtotal de 1 unidade (sem multiplicar quantidade)
    unit_price = product.calculate_total_price(
        quantity=1,
        quantity_kilo=quantity_kilo if quantity_kilo else Decimal("1.0"),
        size=size,
        flavor=flavor,
        topper_text=topper_text,
        roses_quantity=roses_quantity,
    )

    # Salva no session bag
    bag[item_key] = {
        "product_id": product.id,
        "flavor_id": flavor.id if flavor else None,
        "quantity": quantity,
        "quantity_kilo": str(quantity_kilo),
        "size": size or "",
        "topper_text": topper_text or "",
        "topper_price": str(topper_price),
        "roses_quantity": roses_quantity,
        "roses_price_each": str(roses_price_each),
        "roses_price": str(roses_price),
        "message": message or "",
        "message_price": str(message_price),
        "unit_price": str(unit_price),
        "subtotal": str(subtotal),
        "item_key": item_key,
    }

    request.session["bag"] = bag
    messages.success(request, "Product added to your bag!")
    return redirect("view_bag")

def adjust_bag(request, item_key):
    try:
        product = get_object_or_404(Product, pk=item_key)
        quantity = int(request.POST.get('quantity', 0))
        quantity_kilo = float(request.POST.get('quantity_kilo', 0))
        size = request.POST.get('size')
        bag = request.session.get('bag', {})

        if item_key in bag:
            if product.sale_option == "size":
                if size:
                    if quantity > 0:
                        bag[item_key]['quantity'] = quantity
                        bag[item_key]['size'] = size
                        messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {quantity}')
                    else:
                        del bag[item_key]
                        messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
                else:
                    existing_size = bag[item_key].get('size')
                    if existing_size:
                        if quantity > 0:
                            bag[item_key]['quantity'] = quantity
                            messages.success(request, f'Updated size {existing_size.upper()} {product.name} quantity to {quantity}')
                        else:
                            del bag[item_key]
                            messages.success(request, f'Removed size {existing_size.upper()} {product.name} from your bag')
                    else:
                        messages.error(request, "Size is required for this product.")
                        return redirect(reverse('view_bag'))
            elif product.sale_option == "kilo":
                if quantity_kilo > 0:
                    bag[item_key]['quantity_kilo'] = quantity_kilo
                    messages.success(request, f'Updated {product.name} quantity to {quantity_kilo:.2f} kg')
                else:
                    del bag[item_key]
                    messages.success(request, f'Removed {product.name} from your bag')
            else:  # "unit" or "piece"
                if quantity > 0:
                    bag[item_key]['quantity'] = quantity
                    messages.success(request, f'Updated {product.name} quantity to {quantity}')
                else:
                    del bag[item_key]
                    messages.success(request, f'Removed {product.name} from your bag')
        else:
            messages.error(request, f"{product.name} is not in your bag.")
            return redirect(reverse('view_bag'))

        request.session['bag'] = bag
        return redirect(reverse('view_bag'))

    except Exception as e:
        messages.error(request, f"Error adjusting your bag: {str(e)}")
        return redirect(reverse('view_bag'))

    
from django.shortcuts import redirect

def remove_from_bag(request, item_key):
    bag = request.session.get('bag', {})

    if item_key in bag:
        del bag[item_key]
        request.session['bag'] = bag
        request.session['product_count'] = sum(
            item.get('quantity', 0) if item.get('quantity') else 1 for item in bag.values()
        )
        messages.success(request, "Removed item from your bag.")
    else:
        messages.error(request, "Error removing item: Item not found in bag.")

    return redirect('view_bag')


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    # Passa o produto para o template
    return render(request, 'products/product_detail.html', {'product': product})
def clear_bag(request):
    """Remove apenas o carrinho (bag) da sessão."""
    if 'bag' in request.session:
        del request.session['bag']  # Remove a chave 'bag' da sessão
        # Opcional: Atualizar a sessão explicitamente para garantir que a alteração seja salva
        request.session.modified = True

    # Redirecionar o usuário para a página do carrinho ou outra página desejada
    return redirect('view_bag')  # Substitua 'view_bag' pelo nome da URL do carrinho