from django.urls import path
from .views import OrderListView, OrderCreateView, cart_view, my_orders_view, checkout

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("add/", OrderCreateView.as_view(), name="add"),
    path('cart/', cart_view, name='cart'),
    path('my-orders/', my_orders_view, name='my_orders'),
    path('checkout/', checkout, name='checkout'),
]