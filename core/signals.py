from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Notification
from orders.models import Order
from products.models import Product

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance: Order, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f"تم إنشاء طلب جديد #{instance.id} من {instance.customer_name}",
            level=Notification.Level.SUCCESS
        )

@receiver(post_save, sender=Product)
def notify_low_stock(sender, instance: Product, created, **kwargs):
    try:
        threshold = int(getattr(settings, "LOW_STOCK_THRESHOLD", 5))
    except Exception:
        threshold = 5
    try:
        if instance.stock is not None and instance.stock <= threshold and instance.is_active:
            Notification.objects.create(
                message=f"المخزون منخفض للمنتج: {instance.name} (المتبقي {instance.stock})",
                level=Notification.Level.WARNING
            )
    except Exception:
        pass