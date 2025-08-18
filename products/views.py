from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Product, Category

# قائمة المنتجات العامة مع الفلاتر والبحث والـ AJAX
def products_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    # البحث
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # فلتر التصنيف
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # فلتر السعر
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # الترتيب
    sort_by = request.GET.get('sort', '').strip()
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    # AJAX request - return only the grid partial
    if request.headers.get('X-Requested-With') == 'fetch':
        return render(request, 'products/_grid.html', context)
    
    return render(request, 'products/public_list.html', context)

# تفاصيل المنتج العامة
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    
    # Check if product is in favorites (session-based)
    favorites = request.session.get('favorites', [])
    is_favorite = product.id in favorites
    
    return render(request, 'products/product_detail.html', {
        'product': product, 
        'images': images,
        'is_favorite': is_favorite
    })

# تبديل المفضلة (AJAX)
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = int(data.get('product_id', 0))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
    if not Product.objects.filter(id=product_id, is_active=True).exists():
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    favorites = request.session.get('favorites', [])
    
    if product_id in favorites:
        favorites.remove(product_id)
        is_favorite = False
    else:
        favorites.append(product_id)
        is_favorite = True
    
    request.session['favorites'] = favorites
    request.session.modified = True
    
    return JsonResponse({'is_favorite': is_favorite})

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