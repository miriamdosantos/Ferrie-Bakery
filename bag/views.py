from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product, Flavor
from decimal import Decimal
# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product, Flavor
from decimal import Decimal

def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product, Flavor
from decimal import Decimal

def add_to_bag(request, item_id):
    try:
        quantity = int(request.POST.get('quantity', 0))
        quantity_kilo = float(request.POST.get('quantity_kilo', 0))
        redirect_url = request.POST.get('redirect_url', '/')

        print(f"Adding to bag - Item ID: {item_id}, Quantity: {quantity}, Quantity Kilo: {quantity_kilo}")

        product = get_object_or_404(Product, id=item_id)
        print(f"Product found: {product.name}, Price: {product.price}")

        flavor = None
        flavor_id = request.POST.get('flavor')
        if flavor_id:
            flavor = get_object_or_404(Flavor, id=flavor_id)
            print(f"Flavor selected: {flavor.name}")

        size = request.POST.get('size', "standard")
        print(f"Size selected: {size}")

        topper_text = request.POST.get('topper_text', None)
        roses_quantity = int(request.POST.get('roses_quantity', 0))
        print(f"Topper text: {topper_text}, Roses quantity: {roses_quantity}")

        # Calcular o preço total
        total_price = product.calculate_total_price(
            quantity, quantity_kilo, size=size, flavor=flavor, 
            topper_text=topper_text, roses_quantity=roses_quantity
        )
        print(f"Total price calculated: {total_price}")

        bag = request.session.get('bag', {})

        if item_id in bag:
            bag[item_id]['quantity'] += quantity
            bag[item_id]['quantity_kilo'] += quantity_kilo
            bag[item_id]['total_price'] = float(total_price)
            bag[item_id]['flavor'] = flavor.name if flavor else None
            print(f"Updated existing item in bag: {bag[item_id]}")
        else:
            bag[item_id] = {
                'quantity': quantity,
                'quantity_kilo': quantity_kilo,
                'total_price': float(total_price),
                'product_name': product.name,
                'flavor': flavor.name if flavor else None,
                'size': size,
                'topper_text': topper_text,
                'roses_quantity': roses_quantity,
            }
            print(f"Added new item to bag: {bag[item_id]}")

        request.session['bag'] = bag
        print(f"Updated session bag: {bag}")

        messages.success(request, f"Added {quantity}x and {quantity_kilo}kg of {product.name} to your bag!")

        return redirect(redirect_url)

    except Exception as e:
        print(f"Error in add_to_bag: {e}")
        messages.error(request, "Failed to add item to the bag. Please try again.")
        return redirect(request.POST.get('redirect_url', '/'))


def clear_bag(request):
    """Remove apenas o carrinho (bag) da sessão."""
    if 'bag' in request.session:
        del request.session['bag']  # Remove a chave 'bag' da sessão
        # Opcional: Atualizar a sessão explicitamente para garantir que a alteração seja salva
        request.session.modified = True

    # Redirecionar o usuário para a página do carrinho ou outra página desejada
    return redirect('view_bag')  # Substitua 'view_bag' pelo nome da URL do carrinho