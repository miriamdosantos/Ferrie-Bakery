from django.shortcuts import render, get_object_or_404
from decimal import Decimal, InvalidOperation
from django.db.models import Min
from decimal import Decimal
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, PersonalizedCakeOrder
from .forms import ProductForm, PersonalizedCakeForm
from checkout.models import Order, OrderLineItem
from profiles.models import UserProfile
from bag.views import add_to_bag
from .models import Flavor, PersonalizedCakeOrder

import logging

logger = logging.getLogger(__name__)




def all_products(request):
    """Exibe todos os produtos por padrão e aplica filtro se houver busca."""

    query = request.GET.get('q', '').strip()  # Captura e remove espaços extras

    if query:  # Se houver uma busca
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(flavor__icontains=query) |  # Agora filtra por sabor (flavor)
            Q(category__name__icontains=query)  # Filtra por nome da categoria
        )
        if not products.exists():  # Se nenhum produto for encontrado
            messages.info(request, "No products found matching your search.")
            return redirect(reverse('home'))  # Redireciona para a home
    elif 'q' in request.GET:  # Se o usuário buscou mas não digitou nada
        messages.warning(request, "Please enter a search term.")
        return redirect(reverse('home'))  # Redireciona para a home
    else:
        products = Product.objects.all()  # Exibe todos os produtos se não houver busca

    context = {'products': products, 'search_query': query}
    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """A view to show individual product details."""
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.all()
    avg_rating = product.get_average_rating()
    
    truffled_flavors = product.flavors.filter(is_truffled=True)
    traditional_flavors = product.flavors.filter(is_truffled=False)

    # Inicializa variáveis de preço
    size_prices = {}
    base_price = product.price

    # Preços por tamanho, se aplicável
    if product.sale_option == "size":
        size_prices = {
            'small': product.calculate_price_by_size('small'),
            'medium': product.calculate_price_by_size('medium'),
            'large': product.calculate_price_by_size('large'),
        }

    # Preço tradicional e truffled (considerando 1 unidade)
    traditional_price = product.calculate_total_price(
        quantity=1,
        flavor=traditional_flavors.first() if traditional_flavors.exists() else None
    )
    truffled_price = product.calculate_total_price(
        quantity=1,
        flavor=truffled_flavors.first() if truffled_flavors.exists() else None
    )

    context = {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "truffled_flavors": truffled_flavors,
        "traditional_flavors": traditional_flavors,
        "traditional_price": traditional_price,
        "truffled_price": truffled_price,
        "base_price": base_price,
        "size_prices": size_prices,
        "stars_range": range(1, 6),
    }

    return render(request, "products/product_detail.html", context)

from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def products_by_category(request, slug=None):
    """
    Exibe uma lista de produtos, filtrando por categoria se um slug de categoria for fornecido.
    """
    products = Product.objects.all()
    category = None
    no_more_items_message = None  # Inicializa a mensagem

    if slug:
        if slug == 'all-cakes':
            categories = Category.objects.filter(name__in=['Birthday Cake', 'Wedding Cake'])
            products = products.filter(category__in=categories)
            category = "All Cakes"  # String, não objeto Category
        elif slug == 'all-desserts':
            categories = Category.objects.filter(name__in=['Cakes in a Pot', 'Mousses', 'Pies'])
            products = products.filter(category__in=categories)
            category = "All Desserts"  # String, não objeto Category
        else:
            category = get_object_or_404(Category, slug=slug)
            products = products.filter(category=category)

        # Verifica se há apenas um produto (APÓS o filtro)
        if products.count() == 1:
            no_more_items_message = "Option currently available, with more exciting choices coming soon!"

    context = {
        'products': products,
        'category': category,  # Pode ser um objeto Category ou uma string
        'no_more_items_message': no_more_items_message,  # Adiciona a mensagem ao contexto
    }
    
    return render(request, 'products/category_products.html', context)

@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


def edit_product(request, product_id):
    """ Edit a product in the store """
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)

@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
# Pedido genérico (do menu principal)





@login_required
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

def safe_decimal(value):
    try:
        return Decimal(str(value))
    except (TypeError, ValueError):
        return Decimal('0.00')

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def create_personalized_cake(request):
    product, _ = Product.objects.get_or_create(
        name="Personalized Cake",
        defaults={"price": 50, "sale_option": "weight"}
    )

    if request.method == "POST":
        form = PersonalizedCakeForm(request.POST, request.FILES)
        if form.is_valid():
            # Cria e salva o bolo personalizado no banco
            order = form.save(commit=True)
            order.user = request.user
            order.save()  # garante que o order está salvo

            # Extrai os dados para a bag
            quantity_kilo = safe_decimal(order.quantity_kilo)
            topper_text = order.topper_text or ''
            roses_quantity = safe_int(order.roses_quantity)
            message = order.message or ''
            flavor = order.flavor

            # Calcula subtotal do item
            subtotal = safe_decimal(product.price) * quantity_kilo
            subtotal += Decimal('5.00') if topper_text else Decimal('0.00')
            subtotal += Decimal('2.00') * Decimal(roses_quantity)
            subtotal += Decimal('10.00') if message else Decimal('0.00')

            # Monta a chave única da bag
            item_key = f"personalized_{order.id}_flavor_{flavor.id if flavor else 'none'}_topper_{topper_text}_roses_{roses_quantity}"

            # Recupera ou cria a bag
            bag = request.session.get("bag", {})

            # Adiciona item à bag
            bag[item_key] = {
                'product_id': product.id,
                'quantity': 1,  # sempre 1
                'quantity_kilo': float(quantity_kilo),
                'price': float(product.price),
                'subtotal': float(subtotal),
                'product_name': product.name,
                'flavor': flavor.name if flavor else None,
                'size': None,
                'topper_text': topper_text,
                'topper_price': float(5 if topper_text else 0),
                'roses_quantity': roses_quantity,
                'roses_price_each': float(2),
                'roses_price': float(2 * roses_quantity),
                'message': message,
                'message_price': float(10 if message else 0),
                'photo_url': order.photo.url if order.photo else None,
            }

            request.session["bag"] = bag
            # Atualiza contagem de produtos de forma segura
            request.session['product_count'] = sum(
                safe_int(item.get('quantity')) + safe_int(item.get('quantity_kilo'))
                for item in bag.values()
            )

            messages.success(request, f"{product.name} added to your bag!")
            return redirect("view_bag")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PersonalizedCakeForm()

    return render(request, "products/personalized_cake_form.html", {"form": form, "product": product})