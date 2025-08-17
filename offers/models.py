from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product

class Offer(models.Model):
    # ربط العرض بمنتج معين (إجباري)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name='المنتج'
    )

    # عنوان العرض (إجباري)
    title = models.CharField('عنوان العرض', max_length=255)

    # نسبة الخصم
    discount_percent = models.PositiveIntegerField(
        'نسبة الخصم (%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )

    # هل العرض فعّال؟
    active = models.BooleanField('مفعّل', default=True)

    # تاريخ إنشاء العرض
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'عرض'
        verbose_name_plural = 'العروض'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.product.name} ({self.discount_percent}%)"