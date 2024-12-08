from django.shortcuts import render
from .models import StoreUpdate
from products.models import Product
# Create your views here.



def index(request):
    products = Product.objects.all()
    stores_updates = StoreUpdate.objects.all()
    best_sellers = Product.objects.filter(is_best_seller=True)
    
    # Processar os produtos com os cálculos de estrelas
    
    context = {
        'best_sellers': best_sellers ,
        'stars_range': range(1, 6),
        'products' : products,
        'stores_updates': stores_updates
    }
    return render(request, 'home/index.html', context)
