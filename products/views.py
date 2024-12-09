from django.shortcuts import render, get_object_or_404
from .models import Product

# Create your views here.

def all_products(request):
    """ A view to show individual product details"""

    products = Product.objects.all()

    context = {
        'products': products,
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