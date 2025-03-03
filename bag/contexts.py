from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product, Flavor

def bag_contents(request):
    bag = request.session.get('bag', {})  # Recupera o carrinho da sessão
    total = Decimal('0.00')  # Total inicial
    bag_items = []  # Lista para armazenar os itens do carrinho

    for item_key, item_data in bag.items():
        print(f"Item Key: {item_key}, Item Data: {item_data}")  # Depuração

        # Extraímos o ID do produto da chave do item (a chave contém o ID, tamanho e sabor)
        item_key_parts = item_key.split('_')
        product_id = item_key_parts[0]  # O ID é a primeira parte da chave

        try:
            # Garante que estamos buscando o produto correto, já que o ID é um número.
            product = Product.objects.get(id=int(product_id))  # Convertendo para int para garantir que seja um número
        except Product.DoesNotExist:
            print(f"Produto com ID {product_id} não encontrado.")
            continue
        except Product.MultipleObjectsReturned:
            print(f"Erro: Múltiplos produtos com ID {product_id} encontrados.")
            continue
        except ValueError:
            print(f"Erro de valor: ID do produto '{product_id}' não é válido.")
            continue
        except Exception as e:
            print(f"Erro inesperado ao buscar produto {product_id}: {e}")
            continue

        # 🛠️ Verificação do sabor
        flavor = None
        flavor_name = item_data.get('flavor')
        is_trufado = False  # Default

        if flavor_name:
            try:
                flavor = Flavor.objects.get(name=flavor_name)
                is_truffled = flavor.is_truffled  # Pega o atributo is_trufado do Flavor
            except Flavor.DoesNotExist:
                print(f"Sabor com nome '{flavor_name}' não encontrado.")

        # Condicional de preço com base na opção de tamanho
        if product.sale_option == "size" and item_data.get("size"):
            price = product.calculate_price_by_size(item_data["size"])
        else:
            price = product.price

        # Garantindo valores padrão antes do cálculo
        size = item_data.get('size', '')
        quantity = item_data.get('quantity', 1)
        quantity_kilo = item_data.get('quantity_kilo', 0)
        topper_text = item_data.get('topper_text', '')
        roses_quantity = item_data.get('roses_quantity', 0)

        # Recalcular preço com valores seguros
        recalculated_price = product.calculate_total_price(
            size=size,
            quantity=quantity,
            quantity_kilo=quantity_kilo,
            flavor=flavor,
            topper_text=topper_text,
            roses_quantity=roses_quantity,
            is_truffled=is_trufado  # Adicione esta linha

        )

        # Recuperar preços do topper e das rosas com métodos do produto
        topper_price = product.get_topper_price()  # Método para obter o preço do topper
        roses_price = product.get_roses_price(roses_quantity)  # Preço total das rosas
        roses_price_each = product.get_roses_price(roses_quantity, return_individual=True)  # Preço individual de cada rosa

        subtotal = Decimal(recalculated_price) + topper_price  # Sem adicionar rosas aqui
        total += subtotal  

        # Ajustando imagem com segurança
        image_url = product.image.url if product.image else None


        # Atualizando bag_items para incluir os preços de topper e rosas
        bag_items.append({
            'product': product,
            'quantity': quantity,
            'quantity_kilo':quantity_kilo,
            'size': size,
            "price": Decimal(price), 
            'flavor': flavor,
            'is_truffled': is_trufado, 
            'topper_text': topper_text,  # Garante que topper_text seja passado
            'roses_quantity': roses_quantity,  # Garante que roses_quantity seja passado
            'image': image_url,
            'subtotal': subtotal,
            'topper_price': topper_price,  # Preço do topper no contexto
            'roses_price': roses_price,  # Preço total das rosas no contexto
            'roses_price_each': roses_price_each,  # Preço individual de cada rosa
            'item_key': item_key,
        })

        print(f"Produto: {product.name}, Subtotal calculado: {subtotal}")
        print(request.session.get("bag"))

    # Cálculo do frete
    delivery = Decimal('0')
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
    grand_total = total + delivery

    product_count = sum(item['quantity'] for item in bag.values())

    # Contexto com os valores necessários
    context = {
        'bag_items': bag_items,
        'total': total,
        'delivery': delivery,  
        'free_delivery_delta': settings.FREE_DELIVERY_THRESHOLD - total if total < settings.FREE_DELIVERY_THRESHOLD else 0,
        'grand_total': grand_total,  
        'product_count': product_count,
    }

    return context
