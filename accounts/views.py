from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import RegisterForm, LoginForm
from orders.models import Order
from products.models import Favorite

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            # محاولة تسجيل الدخول باسم المستخدم أولاً
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                # حاول البحث بالبريد الإلكتروني
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            if user:
                login(request, user)
                return redirect('home')
            else:
                error = 'بيانات الدخول غير صحيحة.'
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'error': error})

@login_required
def account_view(request):
    """صفحة الحساب الشخصي"""
    user = request.user
    
    # جلب طلبات المستخدم
    orders = Order.objects.filter(user=user).order_by('-created_at')
    orders_paginator = Paginator(orders, 10)
    orders_page_number = request.GET.get('orders_page')
    orders_page_obj = orders_paginator.get_page(orders_page_number)
    
    # جلب المفضلات
    favorites = Favorite.objects.filter(user=user).select_related('product').order_by('-created_at')
    favorites_paginator = Paginator(favorites, 12)
    favorites_page_number = request.GET.get('favorites_page')
    favorites_page_obj = favorites_paginator.get_page(favorites_page_number)
    
    # إحصائيات
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    total_favorites = favorites.count()
    
    context = {
        'orders': orders_page_obj,
        'favorites': favorites_page_obj,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_favorites': total_favorites,
    }
    
    return render(request, 'accounts/account.html', context)