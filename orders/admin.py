from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "unit_price", "total_price")
    readonly_fields = ("total_price",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "status", "payment_method", "total", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    
    fieldsets = (
        ("معلومات العميل", {
            "fields": ("user", "customer_name", "customer_phone", "customer_email")
        }),
        ("عنوان التسليم", {
            "fields": ("customer_address", "customer_city")
        }),
        ("تفاصيل الطلب", {
            "fields": ("total", "payment_method", "status", "order_notes")
        }),
        ("التواريخ", {
            "fields": ("created_at", "updated_at")
        }),
    )
