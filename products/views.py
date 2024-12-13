from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Min

def all_products(request):
    """A view to show the first product of each category."""
    
    # Obtem todas as categorias com o menor ID de produto para cada uma
    products = (
        Product.objects
        .values('category')
        .annotate(first_product_id=Min('id'))  # Identifica o menor ID de produto por categoria
        .values_list('first_product_id', flat=True)  # Pega apenas os IDs dos primeiros produtos
    )
    
    # Filtra os produtos com base nos IDs obtidos
    unique_products = Product.objects.filter(id__in=products)
    
    context = {
        'products': unique_products,
        'stars_range': range(1, 6),
    }

    return render(request, 'products/products.html', context)

def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.all()  # Todas as reviews associadas ao produto
    avg_rating = product.get_average_rating()  # Média das reviews

    context = {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "stars_range": range(1, 6),  # Usado para representar estrelas no template
    }

    return render(request, 'products/product_detail.html', context)


def products_by_category(request, slug):
    if slug == 'all-cakes' :
        # Lógica para buscar todos os bolos
        products = Product.objects.filter(category__name__in=['Birthday Cake', 'Wedding Cake'])
        category = 'All Cakes'
    if slug == 'all-desserts':
        products = Product.objects.filter(category__name__in=['Cakes in a Pot', 'Mousses','Pies'])
        category = 'All Desserts'
    else:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/products.html', context)
