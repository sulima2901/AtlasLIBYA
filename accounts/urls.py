from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import register_view, login_view

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('', include('django.contrib.auth.urls')),  # هنا تضمن جميع المسارات الافتراضية لدجانغو (مثلاً reset password)
]