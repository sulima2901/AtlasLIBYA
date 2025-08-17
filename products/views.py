from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Category, Favorite
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from .models import Product, Category, Favorite
import json

# قائمة المنتجات العامة
def products_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    
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
    
    # فلترة حسب العلامة التجارية
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand__iexact=brand_filter)
    
    # فلترة حسب السعر
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass
    
    # فلاتر خاصة
    if request.GET.get('new'):
        from datetime import datetime, timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        products = products.filter(created_at__gte=thirty_days_ago)
    
    if request.GET.get('offers'):
        products = products.filter(Q(is_on_offer=True) | Q(discount_percent__gt=0))
    
    # الترتيب
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'name', 'price', '-price']:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('-created_at')
    
    # الصفحات
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # قائمة العلامات التجارية المتاحة للفلترة
    brands = Product.objects.filter(is_active=True, brand__isnull=False).exclude(brand='').values_list('brand', flat=True).distinct().order_by('brand')
    
    # نطاق الأسعار
    price_range = Product.objects.filter(is_active=True).aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # الفلاتر المفعلة (لعرض الشيبس)
    active_filters = {}
    if search_query:
        active_filters['search'] = search_query
    if category_filter:
        try:
            cat_obj = Category.objects.get(slug=category_filter)
            active_filters['category'] = {'slug': category_filter, 'name': cat_obj.name}
        except Category.DoesNotExist:
            pass
    if brand_filter:
        active_filters['brand'] = brand_filter
    if min_price:
        active_filters['min_price'] = min_price
    if max_price:
        active_filters['max_price'] = max_price
    
    return render(request, 'products/public_list.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'price_range': price_range,
        'active_filters': active_filters,
        'search_query': search_query,
        'sort_by': sort_by,
    })

# تفاصيل المنتج العامة
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    return render(request, 'products/product_detail.html', {'product': product, 'images': images})

# ============ سلة مشتريات تعتمد جلسة ============
def _get_cart(request):
    cart = request.session.get('cart', {})
    return cart if isinstance(cart, dict) else {}

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    qty = 1
    if request.method == "POST":
        try:
            qty = int(request.POST.get('qty', '1')) or 1
        except ValueError:
            qty = 1

    if product.stock <= 0:
        messages.error(request, "المنتج غير متوفر حاليًا.")
        return redirect('products:product_detail', slug=product.slug)

    cart = _get_cart(request)
    pid = str(product.id)
    cart[pid] = cart.get(pid, 0) + max(qty, 0)
    _save_cart(request, cart)
    messages.success(request, f"تمت إضافة {product.name} إلى السلة.")
    return redirect('products:view_cart')

def view_cart(request):
    cart = _get_cart(request)
    product_ids = [int(pid) for pid in cart.keys()]
    items, subtotal = [], 0

    products = Product.objects.filter(id__in=product_ids)
    prod_map = {p.id: p for p in products}

    for pid_str, qty in cart.items():
        p = prod_map.get(int(pid_str))
        if not p:
            continue
        unit_price = p.price_after_discount() if hasattr(p, 'price_after_discount') else p.price
        line_total = unit_price * qty
        subtotal += line_total
        items.append({"product": p, "qty": qty, "unit_price": unit_price, "line_total": line_total})

    return render(request, 'core/cart.html', {"items": items, "subtotal": subtotal})

def remove_from_cart(request, pk):
    cart = _get_cart(request)
    cart.pop(str(pk), None)
    _save_cart(request, cart)
    messages.info(request, "تمت إزالة المنتج من السلة.")
    return redirect('products:view_cart')

def update_cart(request, pk):
    if request.method != "POST":
        return redirect('products:view_cart')
    cart = _get_cart(request)
    try:
        qty = int(request.POST.get('qty', '1'))
    except ValueError:
        qty = 1
    if qty <= 0:
        cart.pop(str(pk), None)
    else:
        cart[str(pk)] = qty
    _save_cart(request, cart)
    messages.success(request, "تم تحديث الكمية.")
    return redirect('products:view_cart')

# ============ المفضلة ============
@require_POST
@login_required
def toggle_favorite(request):
    """تبديل حالة المفضلة للمنتج"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': 'تمت إضافة المنتج للمفضلة' if is_favorite else 'تمت إزالة المنتج من المفضلة'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'حدث خطأ في العملية'
        }, status=400)

# ============ الشراء الفوري ============
def buy_now(request, pk):
    """الشراء الفوري - ينقل مباشرة لصفحة الدفع"""
    if request.method != "POST":
        return redirect('products:product_detail', slug=get_object_or_404(Product, pk=pk).slug)
    
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    try:
        qty = max(1, int(request.POST.get('qty', '1')))
    except ValueError:
        qty = 1
    
    if product.stock <= 0:
        messages.error(request, "المنتج غير متوفر حاليًا.")
        return redirect('products:product_detail', slug=product.slug)
    
    if qty > product.stock:
        messages.error(request, f"الكمية المطلوبة غير متوفرة. متوفر فقط {product.stock} قطعة.")
        return redirect('products:product_detail', slug=product.slug)
    
    # حفظ معلومات الشراء الفوري في الجلسة
    request.session['buy_now_item'] = {
        'product_id': product.id,
        'quantity': qty,
        'unit_price': float(product.price_after_discount()),
        'total_price': float(product.price_after_discount() * qty)
    }
    
    # التوجه لصفحة الدفع مع معرف الشراء الفوري
    return redirect('orders:checkout')

# ============ صفحة المفضلة ============
@login_required
def favorites_list(request):
    """صفحة المفضلة"""
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/favorites_list.html', {
        'favorites': page_obj
    })