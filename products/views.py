from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import Product, Category, Favorite

# قائمة المنتجات العامة
def products_list(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'products/public_list.html', {
        'products': products,
        'categories': categories,
    })

# تفاصيل المنتج العامة
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    
    # Check if product is favorited by current user
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'products/product_detail.html', {
        'product': product, 
        'images': images,
        'is_favorite': is_favorite
    })

# Toggle favorite functionality
@require_http_methods(["POST"])
def toggle_favorite(request, pk):
    if not request.user.is_authenticated:
        # For anonymous users, use session storage
        favorites = request.session.get('favorites', [])
        product_id = int(pk)
        
        if product_id in favorites:
            favorites.remove(product_id)
            is_favorite = False
            message = "تم إزالة المنتج من المفضلات"
        else:
            favorites.append(product_id)
            is_favorite = True
            message = "تم إضافة المنتج إلى المفضلات"
        
        request.session['favorites'] = favorites
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message,
            'favorites_count': len(favorites)
        })
    
    # For authenticated users, use database
    product = get_object_or_404(Product, pk=pk, is_active=True)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        message = "تم إزالة المنتج من المفضلات"
    else:
        is_favorite = True
        message = "تم إضافة المنتج إلى المفضلات"
    
    favorites_count = Favorite.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'message': message,
        'favorites_count': favorites_count
    })

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

    return render(request, 'orders/cart.html', {"items": items, "subtotal": subtotal})

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