from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "total", "status"]
        labels = {
            "customer_name": "اسم العميل",
            "total": "الإجمالي",
            "status": "الحالة",
        }
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }