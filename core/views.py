from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
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

def offers_list(request):
    """صفحة العروض - عرض المنتجات التي عليها عروض"""
    # احصل على المنتجات في عروض أو عليها خصم
    products = Product.objects.filter(
        is_active=True
    ).filter(
        Q(is_on_offer=True) | Q(discount_percent__gt=0)
    ).select_related('category').order_by('-created_at')
    
    # البحث
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    # فلترة حسب التصنيف
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    # الترتيب
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'name', 'price', '-price']:
        products = products.order_by(sort_by)
    
    # الصفحات
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # إحصائيات للعروض
    total_offers = products.count()
    categories_with_offers = products.values_list('category__name', 'category__slug').distinct()
    
    return render(request, 'core/offers.html', {
        'page_obj': page_obj,
        'products': page_obj,
        'search_query': search_query,
        'total_offers': total_offers,
        'categories_with_offers': categories_with_offers,
        'current_sort': sort_by,
    })