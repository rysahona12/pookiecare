# PookieCare - Skincare E-Commerce Platform

A modern Django-based e-commerce platform for selling skincare products in Bangladesh with a beautiful baby pink UI theme.

## 🎨 Design Features

- **Baby Pink Theme**: Modern gradient design with #ffc0cb, #ffb6c1, #ff69b4, #ff1493
- **Consolas Font**: Professional monospace typography throughout
- **Responsive UI**: Full-width sticky navbar, centered product cards
- **Dynamic Search**: 500ms debounce search with focus preservation
- **Modern Filters**: Sidebar filters with price range, brand, category
- **Product Cards**: Fixed 300×480px cards with 2-line name truncation

## 📁 Project Structure

```
pookiecare/
├── manage.py
├── requirements.txt
├── README.md
├── TEST_COVERAGE_SUMMARY.md      # Test coverage documentation
├── db.sqlite3
├── media/                         # User-uploaded files (product images)
│   └── products/
│       └── images/
├── pookiecare/                    # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── user/                          # User management application
│   ├── models.py                  # Custom User model with UUID
│   ├── views.py                   # Auth & profile views
│   ├── forms.py                   # Registration & profile edit forms
│   ├── admin.py                   # Admin configuration
│   ├── backends.py                # Email authentication backend
│   ├── tests.py                   # 37 comprehensive tests
│   ├── urls.py
│   └── templates/user/
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       └── edit_profile.html
└── products/                      # Products & orders application
    ├── models.py                  # Product, Brand, Category, Order models
    ├── views.py                   # Home, products list, product detail
    ├── admin.py                   # E-commerce admin
    ├── tests.py                   # 41 comprehensive tests
    ├── urls.py
    └── templates/products/
        ├── home.html              # Featured + latest 10 products
        ├── products_list.html     # All products with filters/search
        └── product_detail.html
```

## ✨ Key Features

### User Management
- ✅ **Custom User Model** with UUID primary key
- ✅ **Email Authentication** (login with email, not username)
- ✅ **Bangladeshi Phone Validation** (11-digit format: 01XXXXXXXXX)
- ✅ **Profile Editing** (all fields except email)
- ✅ **Address Management** (house, road, postal code, district)
- ✅ **Full Admin Integration** with custom forms

### Product Management
- ✅ **Brand & Category Organization**
- ✅ **Product Catalog** with local/external image support
- ✅ **Featured Products** section (highlighted on homepage)
- ✅ **Inventory Tracking** with color-coded stock status
- ✅ **Price Management** in BDT (৳)
- ✅ **Image Handling** with padding and object-fit: contain

### E-Commerce Features
- ✅ **Dynamic Search** across product name, brand, category
- ✅ **Advanced Filtering** by brand, category, price range
- ✅ **Sort Options** (Latest, Price Low-High, High-Low)
- ✅ **Shopping Cart System** (orders with in_cart flag)
- ✅ **Automatic Stock Updates** on order completion
- ✅ **Order Management** with quantity tracking

### UI/UX Features
- ✅ **Modern Design** with baby pink gradient theme
- ✅ **Responsive Layout** with sticky navigation
- ✅ **Product Cards** with fixed sizing and truncation
- ✅ **Search Bar** with dynamic submission and focus preservation
- ✅ **Sidebar Filters** with dropdown selects
- ✅ **Stock Badges** (green/orange/red indicators)

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and navigate
git clone https://github.com/rysahona12/pookiecare.git
cd pookiecare

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```
Provide: email, phone (01XXXXXXXXX), name, address, password

### 3. Run Server
```bash
python manage.py runserver
```

### 4. Access Application
- 🏠 **Home**: http://127.0.0.1:8000/
- 🔐 **Login**: http://127.0.0.1:8000/user/login/
- 📝 **Register**: http://127.0.0.1:8000/user/register/
- 👤 **Profile**: http://127.0.0.1:8000/user/profile/
- 🛍️ **Products**: http://127.0.0.1:8000/products/
- ⚙️ **Admin**: http://127.0.0.1:8000/admin/

## 📊 Testing

### Run All Tests (78 tests)
```bash
python manage.py test              # All tests
python manage.py test user.tests   # User tests (37)
python manage.py test products.tests  # Products tests (41)
```

See `TEST_COVERAGE_SUMMARY.md` for detailed test documentation.

## 🛠️ Technology Stack

- **Framework**: Django 5.2.7
- **Database**: SQLite3 (development)
- **Python**: 3.13.7
- **Image Processing**: Pillow 11.0.0
- **Authentication**: Custom email-based backend

## ⚙️ Configuration

Key settings in `pookiecare/settings.py`:

```python
# Custom User Model
AUTH_USER_MODEL = 'user.User'

# Email Authentication
AUTHENTICATION_BACKENDS = [
    'user.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# URLs
LOGIN_URL = 'user:login'
LOGIN_REDIRECT_URL = 'products:home'
LOGOUT_REDIRECT_URL = 'user:login'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 📱 Pages Overview

### Public Pages
- **Home** (`/`): Featured products (6) + Latest 10 products
- **Products List** (`/products/`): All products with search/filters/sort
- **Product Detail** (`/product/<id>/`): Full product info + related products
- **Register** (`/user/register/`): User registration form
- **Login** (`/user/login/`): Email-based authentication

### Authenticated Pages
- **Profile** (`/user/profile/`): View user information
- **Edit Profile** (`/user/profile/edit/`): Update personal info (except email)

### Admin Panel (`/admin/`)
- User management with custom forms
- Brand & Category management
- Product catalog with image previews
- Order management with stock validation
- Color-coded status indicators

## 🔒 Security Features

- ✅ CSRF protection on all forms
- ✅ Secure password hashing (Django's PBKDF2)
- ✅ UUID primary keys (non-sequential)
- ✅ Email & phone uniqueness validation
- ✅ Phone format validation (regex)
- ✅ Login required decorators
- ✅ Session-based authentication

## 📝 Data Models

### User Model
- UUID primary key
- Email (unique, used for login)
- Phone (11-digit Bangladeshi format)
- Name fields (first, middle, last)
- Address (house, road, postal code, district)
- Fixed country: Bangladesh

### Product Models
- **Brand**: UUID, brand name
- **Category**: UUID, category name
- **Product**: UUID, name, image, brand, category, price, stock, featured flag
- **Order**: UUID, user FK, in_cart flag, timestamps
- **OrderItem**: UUID, order FK, product FK, quantity, price snapshot

### Key Methods
- `Product.is_in_stock()` - Check availability
- `Product.get_stock_status()` - Status message
- `Order.get_total_items()` - Total quantity
- `Order.get_total_price()` - Total cost
- `Order.complete_order()` - Process & update stock
- `OrderItem.get_subtotal()` - Line item total

## 🎯 Validation Rules

### Phone Number
- **Format**: 01XXXXXXXXX
- **Length**: Exactly 11 digits
- **Prefix**: Must start with "01"
- **Characters**: Digits only
- **Examples**: 
  - ✅ 01712345678
  - ✅ 01812345678
  - ❌ +8801712345678 (includes country code)
  - ❌ 1712345678 (missing 0)
  - ❌ 0171234567 (only 10 digits)

### Product Images
- Stored in: `media/products/images/`
- Supports: local uploads & external URLs
- Display: object-fit: contain with padding
- Formats: JPEG, PNG, GIF, WebP

## 🔮 Future Enhancements

### Planned Features
- [ ] Password reset via email
- [ ] Email verification on registration
- [ ] Order history for customers
- [ ] Shopping cart UI
- [ ] Checkout flow
- [ ] Payment gateway (bKash, Nagad, SSL Commerz)
- [ ] Product reviews & ratings
- [ ] Wishlist functionality
- [ ] Discount codes
- [ ] Email/SMS notifications
- [ ] Advanced analytics dashboard
- [ ] REST API for mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 📧 Contact

Repository: [rysahona12/pookiecare](https://github.com/rysahona12/pookiecare)

---

**Note**: This platform is specifically designed for the Bangladesh market with localized features (phone format, BDT currency, Bangladesh-only shipping).
