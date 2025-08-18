from django.shortcuts import render
from products.models import Product

def home(request):
    # صفحة رئيسية عامة، تعرض أحدث المنتجات المفعّلة
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
    
    return render(request, 'core/home.html', {
        'products': products,
        'new_products': new_products,
    })