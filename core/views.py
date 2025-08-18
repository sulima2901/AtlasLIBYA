from django.shortcuts import render
from products.models import Product

def home(request):
    # صفحة رئيسية عامة، تعرض أحدث المنتجات المفعّلة
    # المنتجات الجديدة (آخر 30 يوماً)
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:12]
    
    # المنتجات التي عليها عروض
    offer_products = Product.objects.filter(
        is_active=True, 
        is_on_offer=True
    ).order_by('-created_at')[:12]
    
    return render(request, 'core/home.html', {
        'new_products': new_products,
        'offer_products': offer_products,
    })