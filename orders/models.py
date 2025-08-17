from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد المعالجة'
        PAID = 'paid', 'مدفوع'
        SHIPPED = 'shipped', 'تم الشحن'
        DELIVERED = 'delivered', 'تم التسليم'
        CANCELED = 'canceled', 'ملغي'

    class PaymentMethod(models.TextChoices):
        COD = 'cod', 'الدفع عند الاستلام'
        # يمكن إضافة طرق دفع أخرى لاحقاً

    # معلومات العميل
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField('الاسم الكامل', max_length=255)
    customer_phone = models.CharField('رقم الهاتف', max_length=20, default='')
    customer_email = models.EmailField('البريد الإلكتروني', blank=True, default='')
    customer_address = models.TextField('العنوان', default='')
    customer_city = models.CharField('المدينة/المنطقة', max_length=100, default='')
    order_notes = models.TextField('ملاحظات الطلب', blank=True, default='')
    
    # معلومات الطلب
    total = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField('طريقة الدفع', max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    status = models.CharField('الحالة', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} - {self.customer_name}'

class OrderItem(models.Model):
    """عناصر الطلب"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('الكمية', default=1)
    unit_price = models.DecimalField('سعر الوحدة', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"