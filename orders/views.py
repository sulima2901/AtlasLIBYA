from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Order
from .forms import OrderForm
from django.shortcuts import render

def cart_view(request):
    return render(request, 'orders/cart.html')

def my_orders_view(request):
    # يمكنك لاحقًا جلب الطلبات الخاصة بالمستخدم من قاعدة البيانات هنا
    return render(request, 'orders/my_orders.html')

def products_list(request):
    # يمكنك لاحقًا جلب المنتجات من قاعدة البيانات
    return render(request, "products/products_list.html")

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