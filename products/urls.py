from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # واجهة عامة
    path('', views.products_list, name='products_list'),
    path('detail/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # API endpoints
    path('api/filter/', views.products_filter_api, name='products_filter_api'),

    # السلة (جلسة)
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    
    # المفضلة
    path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    
    # شراء فوري
    path('buy-now/<int:pk>/', views.buy_now, name='buy_now'),
]