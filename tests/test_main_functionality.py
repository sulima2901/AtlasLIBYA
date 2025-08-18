from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product, Category, Favorite
from orders.models import Order, OrderItem


class ProductTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="لابتوبات", slug="laptops")
        self.product = Product.objects.create(
            name="لابتوب HP",
            category=self.category,
            brand="HP",
            price=1500.00,
            stock=10,
            description="لابتوب عالي الجودة"
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_product_creation(self):
        """اختبار إنشاء منتج"""
        self.assertEqual(self.product.name, "لابتوب HP")
        self.assertEqual(self.product.brand, "HP")
        self.assertEqual(self.product.price, 1500.00)
        self.assertTrue(self.product.is_active)

    def test_product_slug_generation(self):
        """اختبار توليد slug تلقائيا"""
        self.assertTrue(self.product.slug)

    def test_price_after_discount(self):
        """اختبار حساب السعر بعد الخصم"""
        # بدون خصم
        self.assertEqual(self.product.price_after_discount(), 1500.00)
        
        # مع خصم عادي
        self.product.discount_percent = 10
        self.assertEqual(self.product.price_after_discount(), 1350.00)
        
        # مع عرض خاص
        self.product.is_on_offer = True
        self.product.offer_price = 1200.00
        self.assertEqual(self.product.price_after_discount(), 1200.00)

    def test_is_new_product(self):
        """اختبار تحديد ما إذا كان المنتج جديداً"""
        self.assertTrue(self.product.is_new())


class FavoritesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="لابتوبات", slug="laptops")
        self.product = Product.objects.create(
            name="لابتوب HP",
            category=self.category,
            price=1500.00,
            stock=10
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_favorite_toggle_requires_login(self):
        """اختبار أن المفضلة تتطلب تسجيل الدخول"""
        response = self.client.post('/products/favorites/toggle/', 
                                  {'product_id': self.product.id})
        self.assertEqual(response.status_code, 302)  # إعادة توجيه للدخول

    def test_favorite_toggle_authenticated(self):
        """اختبار تبديل المفضلة للمستخدم المسجل"""
        self.client.login(username='testuser', password='testpass123')
        
        # إضافة للمفضلة
        response = self.client.post('/products/favorites/toggle/', 
                                  {'product_id': self.product.id},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Favorite.objects.filter(user=self.user, product=self.product).exists())
        
        # إزالة من المفضلة
        response = self.client.post('/products/favorites/toggle/', 
                                  {'product_id': self.product.id},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Favorite.objects.filter(user=self.user, product=self.product).exists())


class CartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="لابتوبات", slug="laptops")
        self.product = Product.objects.create(
            name="لابتوب HP",
            category=self.category,
            price=1500.00,
            stock=10
        )

    def test_add_to_cart(self):
        """اختبار إضافة منتج للسلة"""
        response = self.client.post(f'/products/add-to-cart/{self.product.id}/')
        self.assertEqual(response.status_code, 302)  # إعادة توجيه للسلة
        
        # التحقق من وجود المنتج في الجلسة
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.product.id), cart)

    def test_add_out_of_stock_product(self):
        """اختبار إضافة منتج غير متوفر"""
        self.product.stock = 0
        self.product.save()
        
        response = self.client.post(f'/products/add-to-cart/{self.product.id}/')
        self.assertEqual(response.status_code, 302)
        
        # التحقق من عدم إضافة المنتج للسلة
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)


class OrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="لابتوبات", slug="laptops")
        self.product = Product.objects.create(
            name="لابتوب HP",
            category=self.category,
            price=1500.00,
            stock=10
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_checkout_with_empty_cart(self):
        """اختبار الدفع مع سلة فارغة"""
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 302)  # إعادة توجيه للسلة

    def test_checkout_with_items(self):
        """اختبار صفحة الدفع مع عناصر"""
        # إضافة منتج للسلة
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()
        
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_order_creation(self):
        """اختبار إنشاء طلب"""
        # إضافة منتج للسلة
        session = self.client.session
        session['cart'] = {str(self.product.id): 1}
        session.save()
        
        order_data = {
            'customer_name': 'أحمد محمد',
            'customer_phone': '0912345678',
            'customer_email': 'ahmed@example.com',
            'customer_address': 'شارع الجامعة',
            'customer_city': 'طرابلس',
            'order_notes': 'توصيل سريع'
        }
        
        response = self.client.post('/orders/checkout/', order_data)
        
        # التحقق من إنشاء الطلب
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer_name, 'أحمد محمد')
        self.assertEqual(order.total, 1500.00)
        
        # التحقق من إنشاء عناصر الطلب
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 1)


class ProductFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category1 = Category.objects.create(name="لابتوبات", slug="laptops")
        self.category2 = Category.objects.create(name="الهواتف", slug="phones")
        
        self.product1 = Product.objects.create(
            name="لابتوب HP",
            category=self.category1,
            brand="HP",
            price=1500.00,
            stock=10
        )
        self.product2 = Product.objects.create(
            name="لابتوب Dell",
            category=self.category1,
            brand="Dell",
            price=2000.00,
            stock=5
        )
        self.product3 = Product.objects.create(
            name="iPhone",
            category=self.category2,
            brand="Apple",
            price=3000.00,
            stock=8
        )

    def test_category_filter(self):
        """اختبار فلترة حسب التصنيف"""
        response = self.client.get('/products/?category=laptops')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لابتوب HP")
        self.assertContains(response, "لابتوب Dell")
        self.assertNotContains(response, "iPhone")

    def test_brand_filter(self):
        """اختبار فلترة حسب العلامة التجارية"""
        response = self.client.get('/products/?brand=HP')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لابتوب HP")
        self.assertNotContains(response, "لابتوب Dell")

    def test_price_filter(self):
        """اختبار فلترة حسب السعر"""
        response = self.client.get('/products/?min_price=1000&max_price=1800')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لابتوب HP")
        self.assertNotContains(response, "لابتوب Dell")
        self.assertNotContains(response, "iPhone")

    def test_search_functionality(self):
        """اختبار البحث"""
        response = self.client.get('/products/?q=HP')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لابتوب HP")
        self.assertNotContains(response, "لابتوب Dell")