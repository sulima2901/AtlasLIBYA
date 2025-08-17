from django import forms
from .models import Offer
from products.models import Product

class OfferForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),  # تم التعديل هنا
        required=True,
        label='المنتج',
        empty_label='اختر منتجًا',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    title = forms.CharField(
        label='عنوان العرض',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان العرض'}),
    )
    discount_percent = forms.IntegerField(
        label='نسبة الخصم (%)',
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 20'}),
    )
    active = forms.BooleanField(
        label='مفعّل',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = Offer
        fields = ['product', 'title', 'discount_percent', 'active']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # إذا العنوان فارغ، عيّن اسم المنتج تلقائيًا
        if not title and self.cleaned_data.get('product'):
            return self.cleaned_data['product'].name
        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        # لو العنوان فارغ، عيّنه باسم المنتج
        if not instance.title and instance.product:
            instance.title = instance.product.name
        if commit:
            instance.save()
        return instance