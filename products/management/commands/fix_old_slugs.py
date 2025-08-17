from django.core.management.base import BaseCommand
from products.models import Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Generate missing slugs for products'

    def handle(self, *args, **kwargs):
        products = Product.objects.filter(slug__isnull=True) | Product.objects.filter(slug="")
        count = 0
        for product in products:
            base_slug = slugify(product.name)
            slug = base_slug
            i = 1
            # Ensure slug uniqueness
            while Product.objects.filter(slug=slug).exclude(id=product.id).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            product.slug = slug
            product.save()
            count += 1
            self.stdout.write(self.style.SUCCESS(f'Generated slug for product "{product.name}": {slug}'))
        self.stdout.write(self.style.SUCCESS(f"Done. {count} products updated."))