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
    
    # Check if user has favorited this product
    user_has_favorited = False
    if request.user.is_authenticated:
        user_has_favorited = Favorite.objects.filter(
            user=request.user, 
            product=product
        ).exists()
    
    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:6]
    
    # Generate structured data for SEO
    structured_data = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product.name,
        "description": product.description,
        "brand": {
            "@type": "Brand",
            "name": product.brand if product.brand else "AtlasLY"
        },
        "category": product.category.name if product.category else "",
        "offers": {
            "@type": "Offer",
            "priceCurrency": "LYD",
            "price": float(product.price_after_discount),
            "availability": "https://schema.org/InStock" if product.stock > 0 else "https://schema.org/OutOfStock",
            "seller": {
                "@type": "Organization",
                "name": "AtlasLY"
            }
        }
    }
    
    if images.first():
        structured_data["image"] = request.build_absolute_uri(images.first().image.url)
    
    return render(request, 'products/product_detail.html', {
        'product': product, 
        'images': images,
        'user_has_favorited': user_has_favorited,
        'related_products': related_products,
        'structured_data': json.dumps(structured_data),
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
        
        # Get updated favorites count
        favorites_count = Favorite.objects.filter(user=request.user).count()
            
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'favorites_count': favorites_count,
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

def products_filter_api(request):
    """API endpoint for filtering products with AJAX"""
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    # Category filter (supports multiple categories)
    category_filter = request.GET.get('category')
    if category_filter:
        category_slugs = category_filter.split(',')
        products = products.filter(category__slug__in=category_slugs)
    
    # Brand filter (supports multiple brands)
    brand_filter = request.GET.get('brand')
    if brand_filter:
        brands = brand_filter.split(',')
        products = products.filter(brand__in=brands)
    
    # Price filtering
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
    
    # Special filters
    if request.GET.get('new'):
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timedelta(days=30)
        products = products.filter(created_at__gte=thirty_days_ago)
    
    if request.GET.get('offers'):
        products = products.filter(Q(is_on_offer=True) | Q(discount_percent__gt=0))
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'name', 'price', '-price']:
        products = products.order_by(sort_by)
    else:
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare JSON response
    products_data = []
    for product in page_obj:
        # Get first image
        image_url = None
        first_image = product.images.first()
        if first_image and first_image.image:
            image_url = first_image.image.url
            
        products_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': f"{product.price_after_discount:,.0f}",
            'original_price': f"{product.price:,.0f}" if product.discount_percent > 0 else None,
            'discount_percent': product.discount_percent if product.discount_percent > 0 else None,
            'image': image_url,
            'short_description': product.description[:100] + '...' if product.description and len(product.description) > 100 else product.description,
            'is_new': product.is_new,
            'is_on_offer': product.is_on_offer,
            'category': product.category.name if product.category else None,
            'brand': product.brand,
            'stock': product.stock,
        })
    
    # Pagination info
    pagination = {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_count': paginator.count
    }
    
    return JsonResponse({
        'products': products_data,
        'pagination': pagination,
        'total_count': paginator.count,
        'current_filters': {
            'search': search_query,
            'category': category_filter,
            'brand': brand_filter,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort_by
        }
    })

def cart_update_api(request):
    """API endpoint for updating cart quantities"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        action = data.get('action', 'update')  # 'update', 'add', 'remove'
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID required'})
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = _get_cart(request)
        pid = str(product.id)
        
        if action == 'remove':
            cart.pop(pid, None)
            message = f"تمت إزالة {product.name} من السلة"
        elif action == 'add':
            if product.stock <= 0:
                return JsonResponse({'success': False, 'message': 'المنتج غير متوفر حاليًا'})
            cart[pid] = cart.get(pid, 0) + max(quantity, 1)
            message = f"تمت إضافة {product.name} إلى السلة"
        else:  # update
            if quantity <= 0:
                cart.pop(pid, None)
                message = f"تمت إزالة {product.name} من السلة"
            else:
                if quantity > product.stock:
                    return JsonResponse({
                        'success': False, 
                        'message': f'الكمية المطلوبة غير متوفرة. متوفر فقط {product.stock} قطعة'
                    })
                cart[pid] = quantity
                message = "تم تحديث الكمية"
        
        _save_cart(request, cart)
        
        # Calculate cart summary
        cart_count = sum(cart.values())
        cart_total = 0
        
        if cart:
            product_ids = [int(pid) for pid in cart.keys()]
            products = Product.objects.filter(id__in=product_ids)
            prod_map = {p.id: p for p in products}
            
            for pid_str, qty in cart.items():
                p = prod_map.get(int(pid_str))
                if p:
                    unit_price = p.price_after_discount if hasattr(p, 'price_after_discount') else p.price
                    cart_total += unit_price * qty
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count,
            'cart_total': f"{cart_total:,.2f}",
            'item_quantity': cart.get(pid, 0),
            'item_total': f"{(cart.get(pid, 0) * (product.price_after_discount if hasattr(product, 'price_after_discount') else product.price)):,.2f}" if cart.get(pid) else "0.00"
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'حدث خطأ في العملية'}, status=400)