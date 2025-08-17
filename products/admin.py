from django.contrib import admin
from django.utils.text import slugify
from .models import Category, Product, ProductImage, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "is_on_offer", "offer_price", "stock", "is_active", "created_at")
    list_filter = ("category", "brand", "is_active", "is_on_offer", "created_at")
    search_fields = ("name", "brand", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__name")
    date_hierarchy = "created_at"

admin.site.site_header = "لوحة تحكم AtlasLY"
admin.site.site_title = "AtlasLY Admin"
admin.site.index_title = "مرحباً بك في لوحة تحكم AtlasLY"
