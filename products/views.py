from django.shortcuts import render, get_object_or_404
from django.db.models import Min
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm



def all_products(request):
    """A view to show all products, including search queries"""
    
    products = Product.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            # Corrigindo a lógica de busca
            queries = Q(name__icontains=query) | Q(description__icontains=query) | Q(flavors__name__icontains=query)
            products = products.filter(queries).distinct()
    
    if not products:
        messages.error(request, " Search criteria not found!")
        return redirect(reverse('products'))

    # Se não houver busca, pegue apenas o primeiro produto de cada categoria
    first_product_ids = (
        Product.objects
        .values('category')
        .annotate(first_product_id=Min('id'))
        .values_list('first_product_id', flat=True)
    )
    
    products = products.filter(id__in=first_product_ids)

    context = {
        'products': products,
        'stars_range': range(1, 6),
        'search_term': query,
    }

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

def products_by_category(request, slug):
    if slug == 'all-cakes':
        # Lógica para buscar todos os bolos
        products = Product.objects.filter(category__name__in=['Birthday Cake', 'Wedding Cake'])
        category = 'All Cakes'
    elif slug == 'all-desserts':
        products = Product.objects.filter(category__name__in=['Cakes in a Pot', 'Mousses', 'Pies'])
        category = 'All Desserts'
    else:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)

    # Verifica se há apenas um produto
    no_more_items_message = None
    if products.count() == 1:
        no_more_items_message = "Option currently available, with more exciting choices coming soon!"

    context = {
        'category': category,
        'products': products,
        'no_more_items_message': no_more_items_message,
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