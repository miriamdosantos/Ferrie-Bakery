from django.shortcuts import render, get_object_or_404
from django.db.models import Min
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category


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
    return render(request, 'products/category_products.html', context)
