from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # الموقع العام
    path('', core_views.home, name='home'),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),
    path('offers/', core_views.offers_list, name='offers_list'),
    
    # API endpoints
    path('api/search/', core_views.search_api, name='search_api'),

    # لوحة التحكم - كلها تحت /dashboard/ فقط
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)