from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem
from .forms import OrderForm
from products.models import Product


def _get_cart(request):
    """الحصول على السلة من الجلسة"""
    cart = request.session.get('cart', {})
    return cart if isinstance(cart, dict) else {}


def _clear_cart(request):
    """إفراغ السلة"""
    request.session['cart'] = {}
    request.session.modified = True


def cart_view(request):
    return render(request, 'orders/cart.html')


def my_orders_view(request):
    # يمكنك لاحقًا جلب الطلبات الخاصة بالمستخدم من قاعدة البيانات هنا
    return render(request, 'orders/my_orders.html')


def checkout_view(request):
    """صفحة الدفع"""
    cart = _get_cart(request)
    buy_now_item = request.session.get('buy_now_item')
    
    # تحديد المصدر: سلة عادية أم شراء فوري
    if buy_now_item:
        # شراء فوري
        try:
            product = get_object_or_404(Product, id=buy_now_item['product_id'], is_active=True)
            items = [{
                'product': product,
                'qty': buy_now_item['quantity'],
                'unit_price': buy_now_item['unit_price'],
                'line_total': buy_now_item['total_price']
            }]
            subtotal = buy_now_item['total_price']
        except (KeyError, Product.DoesNotExist):
            messages.error(request, "المنتج المختار غير متوفر.")
            return redirect('products:products_list')
    else:
        # سلة عادية
        if not cart:
            messages.info(request, "سلة المشتريات فارغة.")
            return redirect('products:view_cart')
        
        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        prod_map = {p.id: p for p in products}
        
        items, subtotal = [], 0
        for pid_str, qty in cart.items():
            p = prod_map.get(int(pid_str))
            if not p:
                continue
            unit_price = p.price_after_discount()
            line_total = unit_price * qty
            subtotal += line_total
            items.append({
                "product": p, 
                "qty": qty, 
                "unit_price": unit_price, 
                "line_total": line_total
            })
        
        if not items:
            messages.error(request, "لا توجد منتجات متوفرة في السلة.")
            return redirect('products:view_cart')
    
    if request.method == 'POST':
        # معالجة طلب الدفع
        try:
            with transaction.atomic():
                # إنشاء الطلب
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    customer_name=request.POST.get('customer_name', '').strip(),
                    customer_phone=request.POST.get('customer_phone', '').strip(),
                    customer_email=request.POST.get('customer_email', '').strip(),
                    customer_address=request.POST.get('customer_address', '').strip(),
                    customer_city=request.POST.get('customer_city', '').strip(),
                    order_notes=request.POST.get('order_notes', '').strip(),
                    total=subtotal,
                    payment_method='cod',
                    status='pending'
                )
                
                # إضافة عناصر الطلب
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['qty'],
                        unit_price=item['unit_price'],
                        total_price=item['line_total']
                    )
                
                # تحديث المخزون
                for item in items:
                    product = item['product']
                    product.stock -= item['qty']
                    product.save()
                
                # إفراغ السلة أو إزالة عنصر الشراء الفوري
                if buy_now_item:
                    del request.session['buy_now_item']
                else:
                    _clear_cart(request)
                
                request.session.modified = True
                messages.success(request, f"تم إنشاء الطلب #{order.id} بنجاح!")
                return redirect('orders:checkout_success', order_id=order.id)
                
        except Exception as e:
            messages.error(request, "حدث خطأ أثناء معالجة الطلب. يرجى المحاولة مرة أخرى.")
            return redirect('orders:checkout')
    
    return render(request, 'orders/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'is_buy_now': bool(buy_now_item)
    })


def checkout_success_view(request, order_id):
    """صفحة نجاح الطلب"""
    order = get_object_or_404(Order, id=order_id)
    
    # التأكد من أن المستخدم يحق له رؤية هذا الطلب
    if request.user.is_authenticated:
        if order.user != request.user:
            messages.error(request, "غير مسموح لك بعرض هذا الطلب.")
            return redirect('home')
    
    return render(request, 'orders/checkout_success.html', {'order': order})


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("orders:list")