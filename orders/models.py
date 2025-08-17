from django.db import models

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد المعالجة'
        PAID = 'paid', 'مدفوع'
        SHIPPED = 'shipped', 'تم الشحن'
        CANCELED = 'canceled', 'ملغي'

    customer_name = models.CharField('اسم العميل', max_length=255)
    total = models.DecimalField('الإجمالي', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('الحالة', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} - {self.customer_name}'