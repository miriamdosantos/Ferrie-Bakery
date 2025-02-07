from django.shortcuts import render
from .models import StoreUpdate
from products.models import Product, Flavor  # Supondo que Flavor seja o modelo relacionado

# Create your views here.
def index(request):
    products = Product.objects.all()
    stores_updates = StoreUpdate.objects.all()
    best_sellers = Product.objects.filter(is_best_seller=True)
    
    # Supondo que você esteja buscando os sabores, use filter() ao invés de get()
    # Filtrando sabores trufados e tradicionais com base no campo is_truffled
    truffled_flavors = Flavor.objects.filter(is_truffled=True)
    traditional_flavors = Flavor.objects.filter(is_truffled=False)


    
    context = {
        'best_sellers': best_sellers,
        'stars_range': range(1, 6),
        'products': products,
        'stores_updates': stores_updates,
        'truffled_flavors': truffled_flavors,
        'traditional_flavors': traditional_flavors,
    }
    return render(request, 'home/index.html', context)
