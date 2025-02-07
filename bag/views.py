from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product, Flavor
from decimal import Decimal
from django.http import JsonResponse





def view_bag(request):
    """ A view that renders the bag contents page """
    bag = request.session.get('bag', {})
    product_count = sum(item['quantity'] for item in bag.values()) if bag else 0
    
    return render(request, 'bag/bag.html', {'product_count': product_count})







def add_to_bag(request, item_id):
    try:
        quantity = int(request.POST.get('quantity', 0))
        quantity_kilo = float(request.POST.get('quantity_kilo', 0))
        redirect_url = request.POST.get('redirect_url', '/')
        edit_mode = request.POST.get('edit_mode', 'false') == 'true'
        item_key = request.POST.get('item_key', None)  # Pega o item_key caso esteja editando

        product = get_object_or_404(Product, id=item_id)
        flavor = None
        flavor_id = request.POST.get('flavor')
        if flavor_id:
            flavor = get_object_or_404(Flavor, id=flavor_id)

        size = request.POST.get('size', "standard")
        topper_text = request.POST.get('topper_text', None)
        roses_quantity = int(request.POST.get('roses_quantity', 0))

        total_price = product.calculate_total_price(
            quantity, quantity_kilo, size=size, flavor=flavor,
            topper_text=topper_text, roses_quantity=roses_quantity
        )

        bag = request.session.get('bag', {})

        # Criar um novo item key com todas as propriedades para identificar itens únicos
        new_item_key = f"{item_id}_size_{size}_flavor_{flavor_id if flavor else 'none'}_topper_{topper_text}_roses_{roses_quantity}"

        if edit_mode and item_key in bag:
            # Guarda os dados do item que está sendo editado
            edited_item = bag.pop(item_key)

            # Se o item editado já existe, atualiza a quantidade
            if new_item_key in bag:
                bag[new_item_key]['quantity'] += quantity
                bag[new_item_key]['quantity_kilo'] += quantity_kilo
                bag[new_item_key]['total_price'] = float(total_price)
                messages.success(request, f"Updated {product.name} and merged with existing item in your bag!")
            else:
                bag[new_item_key] = {
                    'product_id': product.id,
                    'quantity': quantity,
                    'quantity_kilo': quantity_kilo,
                    'total_price': float(total_price),
                    'product_name': product.name,
                    'flavor': flavor.name if flavor else None,
                    'size': size,
                    'topper_text': topper_text,
                    'roses_quantity': roses_quantity,
                }
                messages.success(request, f"Updated {product.name} in your bag!")
        else:
            # Se o item não está sendo editado, apenas adiciona um novo item
            if new_item_key in bag:
                bag[new_item_key]['quantity'] += quantity
                bag[new_item_key]['quantity_kilo'] += quantity_kilo
                bag[new_item_key]['total_price'] = float(total_price)
                messages.success(request, f"Updated {product.name} in your bag!")
            else:
                bag[new_item_key] = {
                    'product_id': product.id,
                    'quantity': quantity,
                    'quantity_kilo': quantity_kilo,
                    'total_price': float(total_price),
                    'product_name': product.name,
                    'flavor': flavor.name if flavor else None,
                    'size': size,
                    'topper_text': topper_text,
                    'roses_quantity': roses_quantity,
                }
                messages.success(request, f"Added {product.name} to your bag!")

        request.session['bag'] = bag
        request.session['product_count'] = sum(item['quantity'] for item in bag.values())

        return redirect(redirect_url)

    except Exception as e:
        messages.error(request, "Failed to add/update item in the bag.")
        return redirect(request.POST.get('redirect_url', '/'))




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
        item = bag[item_key]
        quantity_removed = item['quantity']
        del bag[item_key]
        request.session['bag'] = bag  # Atualiza a sessão
        
        # Atualiza o product_count na sessão
        product_count = sum(item['quantity'] for item in bag.values())
        request.session['product_count'] = product_count

        messages.success(request, f"Removed item from your bag.")
    else:
        messages.error(request, f"Error removing item: Item not found in bag.")

    return redirect('view_bag')  # Redireciona para a página do carrinho




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