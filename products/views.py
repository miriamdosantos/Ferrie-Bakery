from django.shortcuts import render, get_object_or_404

from django.db.models import Min
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, PersonalizedCakeOrder
from .forms import ProductForm, PersonalizedCakeForm

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
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.all()
    avg_rating = product.get_average_rating()
    truffled_flavors = product.flavors.filter(is_truffled=True)
    traditional_flavors = product.flavors.filter(is_truffled=False)

    # Inicializa as variáveis de preço
    base_price = product.price
    size_prices = {}

    # Verifica se o produto deve ter opções de tamanho
    if product.sale_option == "size":
        size_prices = {
            'small': product.calculate_price_by_size('small'),
            'medium': product.calculate_price_by_size('medium'),
            'large': product.calculate_price_by_size('large'),
        }

    # Debug: Verifique se os tamanhos estão sendo passados corretamente
    print(f"Product: {product.name}, Sale Option: {product.sale_option}, Size Prices: {size_prices}")

    context = {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "base_price": base_price,
        "size_prices": size_prices,  # Passa sempre, mesmo que vazio
        "stars_range": range(1, 6),
        'truffled_flavors': truffled_flavors,
        'traditional_flavors': traditional_flavors,
    }

    return render(request, 'products/product_detail.html', context)

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

@login_required
def create_personalized_cake(request, product_slug):
    product = get_object_or_404(Product, category__slug="personalized-cakes", slug=product_slug) if hasattr(Product, "slug") else \
              get_object_or_404(Product, category__slug="personalized-cakes", name=product_slug)

    if request.method == "POST":
        form = PersonalizedCakeForm(request.POST, request.FILES, product=product)
        if form.is_valid():
            order: PersonalizedCakeOrder = form.save(commit=False)
            order.user = request.user
            order.product = product
            order.save()
            messages.success(request, f"Pedido criado! Preço calculado: {order.price_snapshot}.")
            # aqui você pode adicionar ao carrinho, se usar sessão/OrderItem/etc.
            # return redirect("cart:detail")
            return redirect("products:personalized_detail", order_id=order.id)
    else:
        form = PersonalizedCakeForm(product=product)

    context = {
        "product": product,
        "form": form,
    }
    return render(request, "products/create_personalized_cake.html", context)


@login_required
def personalized_detail(request, order_id):
    order = get_object_or_404(PersonalizedCakeOrder, id=order_id, user=request.user)
    return render(request, "products/personalized_detail.html", {"order": order})