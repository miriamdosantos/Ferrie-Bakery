from django.shortcuts import render
from .models import StoreUpdate
# Create your views here.

def index(request):
     """ A view to return the index page """
     store_updates = StoreUpdate.objects.filter(is_active=True)
     context = {"stores_updates": store_updates
     }
     return render(request, 'home/index.html', context)


