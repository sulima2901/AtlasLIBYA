from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard_home(request):
    return render(request, 'dashboard/home.html')
