from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100, blank=True, default="")  # علامة تجارية
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    # حقول العروض الجديدة
    is_on_offer = models.BooleanField(default=False)  # هل المنتج في عرض
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # سعر العرض
    stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)  # إذا false لا يظهر في الموقع العام
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            orig_slug = self.slug
            num = 1
            while Product.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{orig_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)

    def clean(self):
        # التحقق من أن سعر العرض أقل من السعر الأصلي
        if self.offer_price and self.offer_price >= self.price:
            raise ValueError("سعر العرض يجب أن يكون أقل من السعر الأصلي")

    def price_after_discount(self):
        # إذا كان هناك عرض خاص، استخدم سعر العرض
        if self.is_on_offer and self.offer_price:
            return self.offer_price
        # وإلا استخدم الخصم العادي
        if self.discount_percent:
            from decimal import Decimal
            discount_factor = Decimal(str(1 - self.discount_percent / 100))
            return self.price * discount_factor
        return self.price

    def is_new(self):
        """تحديد ما إذا كان المنتج جديداً (أحدث من 30 يوماً)"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.created_at >= thirty_days_ago

    def get_discount_percent(self):
        """حساب نسبة الخصم الفعلية"""
        if self.is_on_offer and self.offer_price:
            return int((1 - self.offer_price / self.price) * 100)
        return self.discount_percent

    def get_savings_amount(self):
        """حساب مبلغ التوفير"""
        if self.is_on_offer and self.offer_price:
            return self.price - self.offer_price
        elif self.discount_percent:
            return self.price * (self.discount_percent / 100)
        return 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.alt_text or f"Image {self.id}"

class Favorite(models.Model):
    """نموذج المفضلات - ربط المستخدم بالمنتج"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # منع التكرار
        verbose_name = 'مفضل'
        verbose_name_plural = 'المفضلات'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"