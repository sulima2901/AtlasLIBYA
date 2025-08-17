from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def dashboard_home(request):
    return render(request, 'dashboard/dashboard_home.html')