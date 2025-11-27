from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from .models import Brand, Category, Product, Order, OrderItem

User = get_user_model()


class BrandModelTestCase(TestCase):
    """Test cases for the Brand model."""
    
    def test_create_brand(self):
        """Test creating a brand."""
        brand = Brand.objects.create(brand_name="CeraVe")
        self.assertEqual(brand.brand_name, "CeraVe")
        self.assertIsNotNone(brand.brand_id)
    
    def test_brand_str(self):
        """Test brand string representation."""
        brand = Brand.objects.create(brand_name="The Ordinary")
        self.assertEqual(str(brand), "The Ordinary")


class CategoryModelTestCase(TestCase):
    """Test cases for the Category model."""
    
    def test_create_category(self):
        """Test creating a category."""
        category = Category.objects.create(category_name="Moisturizers")
        self.assertEqual(category.category_name, "Moisturizers")
        self.assertIsNotNone(category.category_id)
    
    def test_category_str(self):
        """Test category string representation."""
        category = Category.objects.create(category_name="Serums")
        self.assertEqual(str(category), "Serums")


class ProductModelTestCase(TestCase):
    """Test cases for the Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.brand = Brand.objects.create(brand_name="CeraVe")
        self.category = Category.objects.create(category_name="Moisturizers")
    
    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            product_name="CeraVe Moisturizing Cream",
            brand=self.brand,
            category=self.category,
            product_details="<p>Rich moisturizing cream</p>",
            price=Decimal("1250.00"),
            available_stock=50
        )
        self.assertEqual(product.product_name, "CeraVe Moisturizing Cream")
        self.assertEqual(product.price, Decimal("1250.00"))
        self.assertEqual(product.available_stock, 50)
        self.assertFalse(product.featured)
    
    def test_product_is_in_stock(self):
        """Test product stock checking."""
        product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("100.00"),
            available_stock=10
        )
        self.assertTrue(product.is_in_stock())
        
        product.available_stock = 0
        self.assertFalse(product.is_in_stock())
    
    def test_product_stock_status(self):
        """Test product stock status messages."""
        product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("100.00"),
            available_stock=20
        )
        self.assertEqual(product.get_stock_status(), "In Stock")
        
        product.available_stock = 5
        self.assertEqual(product.get_stock_status(), "Low Stock (5 left)")
        
        product.available_stock = 0
        self.assertEqual(product.get_stock_status(), "Out of Stock")


class OrderModelTestCase(TestCase):
    """Test cases for the Order model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            phone_number="01712345678",
            first_name="John",
            last_name="Doe",
            house_number="123",
            road_number="45",
            postal_code="1234",
            district="Dhaka",
            password="testpass123"
        )
        self.brand = Brand.objects.create(brand_name="CeraVe")
        self.category = Category.objects.create(category_name="Moisturizers")
        self.product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("500.00"),
            available_stock=50
        )
    
    def test_create_order(self):
        """Test creating an order."""
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.user, self.user)
        self.assertTrue(order.in_cart)
        self.assertIsNone(order.completed_at)
    
    def test_order_total_items(self):
        """Test calculating total items in order."""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=3,
            price_at_purchase=self.product.price
        )
        self.assertEqual(order.get_total_items(), 3)
    
    def test_order_total_price(self):
        """Test calculating total price of order."""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price_at_purchase=Decimal("500.00")
        )
        self.assertEqual(order.get_total_price(), Decimal("1000.00"))
    
    def test_complete_order(self):
        """Test completing an order and stock update."""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=5,
            price_at_purchase=self.product.price
        )
        
        initial_stock = self.product.available_stock
        success = order.complete_order()
        
        self.assertTrue(success)
        self.assertFalse(order.in_cart)
        self.assertIsNotNone(order.completed_at)
        
        # Refresh product from database
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_stock, initial_stock - 5)
    
    def test_complete_order_insufficient_stock(self):
        """Test order completion fails with insufficient stock."""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=100,  # More than available
            price_at_purchase=self.product.price
        )
        
        success = order.complete_order()
        self.assertFalse(success)
        self.assertTrue(order.in_cart)  # Should still be in cart


class OrderItemModelTestCase(TestCase):
    """Test cases for the OrderItem model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            phone_number="01712345678",
            first_name="John",
            last_name="Doe",
            house_number="123",
            road_number="45",
            postal_code="1234",
            district="Dhaka",
            password="testpass123"
        )
        self.brand = Brand.objects.create(brand_name="CeraVe")
        self.category = Category.objects.create(category_name="Moisturizers")
        self.product = Product.objects.create(
            product_name="Test Product",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("300.00"),
            available_stock=50
        )
        self.order = Order.objects.create(user=self.user)
    
    def test_create_order_item(self):
        """Test creating an order item."""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_at_purchase=self.product.price
        )
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_at_purchase, Decimal("300.00"))
    
    def test_order_item_subtotal(self):
        """Test calculating order item subtotal."""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price_at_purchase=Decimal("300.00")
        )
        self.assertEqual(order_item.get_subtotal(), Decimal("900.00"))
    
    def test_order_item_auto_price(self):
        """Test automatic price setting on save."""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )
        # Price should be automatically set from product
        order_item.refresh_from_db()
        self.assertEqual(order_item.price_at_purchase, self.product.price)


class HomeViewTestCase(TestCase):
    """Test cases for the home view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.home_url = reverse('products:home')
        self.brand = Brand.objects.create(brand_name="CeraVe")
        self.category = Category.objects.create(category_name="Moisturizers")
        
        # Create featured products
        for i in range(8):
            Product.objects.create(
                product_name=f"Featured Product {i}",
                brand=self.brand,
                category=self.category,
                product_details="Test details",
                price=Decimal("500.00"),
                available_stock=10,
                featured=True
            )
        
        # Create regular products
        for i in range(15):
            Product.objects.create(
                product_name=f"Regular Product {i}",
                brand=self.brand,
                category=self.category,
                product_details="Test details",
                price=Decimal("300.00"),
                available_stock=20,
                featured=False
            )
    
    def test_home_page_loads(self):
        """Test home page loads successfully."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/home.html')
    
    def test_home_displays_featured_products(self):
        """Test home displays featured products."""
        response = self.client.get(self.home_url)
        featured_products = response.context['featured_products']
        self.assertEqual(len(featured_products), 6)  # Limited to 6
        for product in featured_products:
            self.assertTrue(product.featured)
    
    def test_home_displays_latest_products(self):
        """Test home displays latest 10 products."""
        response = self.client.get(self.home_url)
        latest_products = response.context['products']
        self.assertEqual(len(latest_products), 10)
    
    def test_home_excludes_out_of_stock(self):
        """Test home excludes out of stock products."""
        Product.objects.create(
            product_name="Out of Stock Product",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("100.00"),
            available_stock=0,
            featured=True
        )
        response = self.client.get(self.home_url)
        products = list(response.context['products']) + list(response.context['featured_products'])
        product_names = [p.product_name for p in products]
        self.assertNotIn("Out of Stock Product", product_names)


class ProductsListViewTestCase(TestCase):
    """Test cases for the products list view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.products_url = reverse('products:products_list')
        
        # Create brands and categories
        self.brand1 = Brand.objects.create(brand_name="CeraVe")
        self.brand2 = Brand.objects.create(brand_name="The Ordinary")
        self.category1 = Category.objects.create(category_name="Moisturizers")
        self.category2 = Category.objects.create(category_name="Serums")
        
        # Create products
        Product.objects.create(
            product_name="CeraVe Moisturizing Cream",
            brand=self.brand1,
            category=self.category1,
            product_details="Test",
            price=Decimal("1250.00"),
            available_stock=10
        )
        Product.objects.create(
            product_name="The Ordinary Niacinamide",
            brand=self.brand2,
            category=self.category2,
            product_details="Test",
            price=Decimal("650.00"),
            available_stock=15
        )
        Product.objects.create(
            product_name="CeraVe Hydrating Cleanser",
            brand=self.brand1,
            category=self.category1,
            product_details="Test",
            price=Decimal("850.00"),
            available_stock=20
        )
    
    def test_products_list_page_loads(self):
        """Test products list page loads successfully."""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/products_list.html')
    
    def test_products_list_displays_all_products(self):
        """Test products list displays all available products."""
        response = self.client.get(self.products_url)
        products = response.context['products']
        self.assertEqual(len(products), 3)
    
    def test_search_by_product_name(self):
        """Test search functionality by product name."""
        response = self.client.get(self.products_url, {'search': 'Moisturizing'})
        products = response.context['products']
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].product_name, "CeraVe Moisturizing Cream")
    
    def test_search_by_brand_name(self):
        """Test search functionality by brand name."""
        response = self.client.get(self.products_url, {'search': 'CeraVe'})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertEqual(product.brand.brand_name, "CeraVe")
    
    def test_search_by_category_name(self):
        """Test search functionality by category name."""
        response = self.client.get(self.products_url, {'search': 'Serums'})
        products = response.context['products']
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category.category_name, "Serums")
    
    def test_search_case_insensitive(self):
        """Test search is case-insensitive."""
        response = self.client.get(self.products_url, {'search': 'cerave'})
        products = response.context['products']
        self.assertEqual(len(products), 2)
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.products_url, {'search': 'NonexistentProduct'})
        products = response.context['products']
        self.assertEqual(len(products), 0)
    
    def test_filter_by_brand(self):
        """Test filtering by brand."""
        response = self.client.get(self.products_url, {'brand': str(self.brand1.brand_id)})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertEqual(product.brand, self.brand1)
    
    def test_filter_by_category(self):
        """Test filtering by category."""
        response = self.client.get(self.products_url, {'category': str(self.category1.category_id)})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertEqual(product.category, self.category1)
    
    def test_filter_by_min_price(self):
        """Test filtering by minimum price."""
        response = self.client.get(self.products_url, {'min_price': '1000'})
        products = response.context['products']
        self.assertEqual(len(products), 1)
        self.assertTrue(all(p.price >= Decimal('1000') for p in products))
    
    def test_filter_by_max_price(self):
        """Test filtering by maximum price."""
        response = self.client.get(self.products_url, {'max_price': '700'})
        products = response.context['products']
        self.assertEqual(len(products), 1)
        self.assertTrue(all(p.price <= Decimal('700') for p in products))
    
    def test_filter_by_price_range(self):
        """Test filtering by price range."""
        response = self.client.get(self.products_url, {'min_price': '600', 'max_price': '900'})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertTrue(Decimal('600') <= product.price <= Decimal('900'))
    
    def test_sort_by_price_low_to_high(self):
        """Test sorting by price low to high."""
        response = self.client.get(self.products_url, {'sort': 'price_low'})
        products = list(response.context['products'])
        prices = [p.price for p in products]
        self.assertEqual(prices, sorted(prices))
    
    def test_sort_by_price_high_to_low(self):
        """Test sorting by price high to low."""
        response = self.client.get(self.products_url, {'sort': 'price_high'})
        products = list(response.context['products'])
        prices = [p.price for p in products]
        self.assertEqual(prices, sorted(prices, reverse=True))
    
    def test_combined_search_and_filters(self):
        """Test combining search with filters."""
        response = self.client.get(self.products_url, {
            'search': 'CeraVe',
            'category': str(self.category1.category_id),
            'max_price': '1000'
        })
        products = response.context['products']
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].product_name, "CeraVe Hydrating Cleanser")
    
    def test_context_preserves_filter_values(self):
        """Test context preserves filter values for form."""
        response = self.client.get(self.products_url, {
            'search': 'test',
            'brand': str(self.brand1.brand_id),
            'min_price': '500',
            'max_price': '1000',
            'sort': 'price_low'
        })
        self.assertEqual(response.context['search_query'], 'test')
        self.assertEqual(response.context['selected_brand'], str(self.brand1.brand_id))
        self.assertEqual(response.context['min_price'], '500')
        self.assertEqual(response.context['max_price'], '1000')
        self.assertEqual(response.context['sort_by'], 'price_low')
    
    def test_brands_and_categories_in_context(self):
        """Test brands and categories are available in context."""
        response = self.client.get(self.products_url)
        self.assertIn('brands', response.context)
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['brands']), 2)
        self.assertEqual(len(response.context['categories']), 2)


class ProductDetailViewTestCase(TestCase):
    """Test cases for the product detail view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.brand = Brand.objects.create(brand_name="CeraVe")
        self.category = Category.objects.create(category_name="Moisturizers")
        self.product = Product.objects.create(
            product_name="CeraVe Moisturizing Cream",
            brand=self.brand,
            category=self.category,
            product_details="<p>Rich moisturizing cream</p>",
            price=Decimal("1250.00"),
            available_stock=10
        )
        
        # Create related products
        for i in range(5):
            Product.objects.create(
                product_name=f"Related Product {i}",
                brand=self.brand,
                category=self.category,
                product_details="Test",
                price=Decimal("500.00"),
                available_stock=10
            )
        
        self.detail_url = reverse('products:product_detail', args=[self.product.product_id])
    
    def test_product_detail_page_loads(self):
        """Test product detail page loads successfully."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
    
    def test_product_detail_displays_correct_product(self):
        """Test product detail displays correct product."""
        response = self.client.get(self.detail_url)
        product = response.context['product']
        self.assertEqual(product.product_id, self.product.product_id)
        self.assertEqual(product.product_name, "CeraVe Moisturizing Cream")
    
    def test_product_detail_displays_related_products(self):
        """Test product detail displays related products."""
        response = self.client.get(self.detail_url)
        related_products = response.context['related_products']
        self.assertEqual(len(related_products), 4)  # Limited to 4
        for product in related_products:
            self.assertEqual(product.category, self.category)
            self.assertNotEqual(product.product_id, self.product.product_id)
    
    def test_product_detail_404_for_invalid_id(self):
        """Test product detail returns 404 for invalid product ID."""
        from uuid import uuid4
        invalid_url = reverse('products:product_detail', args=[uuid4()])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
    
    def test_related_products_exclude_out_of_stock(self):
        """Test related products exclude out of stock items."""
        Product.objects.create(
            product_name="Out of Stock Related",
            brand=self.brand,
            category=self.category,
            product_details="Test",
            price=Decimal("500.00"),
            available_stock=0
        )
        response = self.client.get(self.detail_url)
        related_products = response.context['related_products']
        product_names = [p.product_name for p in related_products]
        self.assertNotIn("Out of Stock Related", product_names)
