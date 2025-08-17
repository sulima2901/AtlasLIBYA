from django.db import models

class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = 'info', 'معلومة'
        SUCCESS = 'success', 'نجاح'
        WARNING = 'warning', 'تحذير'

    message = models.CharField("النص", max_length=255)
    level = models.CharField("المستوى", max_length=10, choices=Level.choices, default=Level.INFO)
    is_read = models.BooleanField("مقروء", default=False)
    created_at = models.DateTimeField("التاريخ", auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"

    def __str__(self):
        return f"[{self.level}] {self.message[:50]}"