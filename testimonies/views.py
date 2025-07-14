from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from .forms import TestimonyForm
from .models import Testimony
from products.models import Product

def add_testimony(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = TestimonyForm(request.POST)
        if form.is_valid():
            testimony = form.save(commit=False)
            testimony.product = product
            testimony.user = request.user
            testimony.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = TestimonyForm()

    return render(request, 'testimonies/add_testimony.html', {'form': form, 'product': product})
