Architecture Overview
=====================

PookieCare is a Django 5.2 project composed of two primary domain apps and a
lightweight project configuration package.

Project Packages
----------------

``pookiecare`` (project configuration)
   Contains global settings, URL routing, and WSGI/ASGI entry points. The
   ``settings.py`` file enables the custom user model, configures email-based
   authentication backends, and defines media storage under ``media/`` for
   product images.

``user`` app
   Manages customer identities using a UUID primary key, email login, Bangladeshi
   phone validation, and full address fields. The app provides registration,
   login/logout, profile display, and profile editing views backed by Django
   forms for both onboarding and updates.

``products`` app
   Owns the commerce catalog. Product assets are grouped by brands and
   categories, and each product tracks stock, featured flag, and pricing in BDT.
   Orders and order items form the shopping cart abstraction. Views render the
   homepage, catalog with search/filter/sort, and product detail pages.

Request Flow
------------

* ``pookiecare.urls`` routes ``/`` to ``products.home_view``, ``/products/`` to the
  catalog view, and ``/product/<uuid>/`` to the detail page.
* Auth routes live under ``/user/`` and are protected with Django's login
  decorators where needed. Successful login redirects to ``user:profile``.
* Static media (uploaded product images) are exposed during development via
  ``django.conf.urls.static``.

Authentication Workflow
-----------------------

1. ``user.views.register_view`` uses ``UserRegistrationForm`` to create accounts
   with validated Bangladeshi phone numbers and full addresses.
2. ``user.backends.EmailBackend`` authenticates via email address so usernames
   never surface.
3. ``login_view`` stores the session and displays a personalized flash message.
4. ``logout_view`` invalidates the session and redirects to the login page.
5. ``LOGIN_URL``/``LOGIN_REDIRECT_URL``/``LOGOUT_REDIRECT_URL`` are centralized
   in ``pookiecare.settings`` so any ``@login_required`` view follows the same
   UX path.

Data Modeling
-------------

* **User** – ``user.models.User`` extends ``AbstractBaseUser`` with UUID primary
  keys, central Bangladeshi address data, and helper methods for full name and
  address formatting.
* **Catalog** – ``products.models.Brand`` and ``Category`` classifications use
  UUID primary keys, alphabetical ordering, and timestamp metadata.
* **Product** – Tracks uploaded or remote imagery, HTML-ready description text,
  and helper methods ``get_image_url()``, ``is_in_stock()``, and
  ``get_stock_status()`` for UI hints.
* **Orders** – ``products.models.Order`` plus ``OrderItem`` implement shopping
  cart semantics. ``Order.complete_order()`` verifies stock, updates product
  quantities, toggles ``in_cart``, and stamps ``completed_at``.

Templates & Styling
-------------------

HTML templates live under ``products/templates/products`` and
``user/templates/user``. Product pages feature a baby pink palette, fixed-size
cards, search input with debounce handling, and sidebar filters for brand,
category, price bounds, and sorting (latest, ascending price, descending price).

Media Handling
--------------

* Uploaded product images live under ``media/products/images/`` and render via
  ``Product.get_image_url()`` (uploaded file wins over external URL).
* ``MEDIA_URL``/``MEDIA_ROOT`` in ``settings.py`` map the storage path, while
  ``urls.py`` exposes them only during development.

Admin Interface
---------------

The Django admin provides the back-office workflow:

* Custom ``UserAdmin`` surfaces authentication, personal info, address, and
  permission groupings plus search + filters tailored for Bangladeshi data.
* ``Brand``/``Category`` list views show product counts and timestamp metadata.
* ``ProductAdmin`` adds inline image previews, currency formatting, and stock
  color badges to quickly identify low or out-of-stock items.
* ``OrderAdmin`` embeds ``OrderItem`` inlines, total price/quantity summaries,
  and a bulk action that calls ``Order.complete_order()`` with stock checks.

Extensibility
-------------

* Additional Django apps (e.g., payments or reviews) can plug into the existing
  project by updating ``INSTALLED_APPS`` and the root ``urls.py``.
* The Sphinx documentation uses autodoc to pull live docstrings from both apps,
  so future modules become part of the API reference without extra wiring once
  they expose docstrings.

Testing & Quality
-----------------

* ``python manage.py test`` runs the full suite (currently 78 tests: 37 ``user``
  + 41 ``products``).
* ``user.tests`` focuses on registration validation, profile editing, and the
  custom authentication backend.
* ``products.tests`` covers catalog filtering/sorting, product detail behavior,
  order management, and stock adjustments.
* ``TEST_COVERAGE_SUMMARY.md`` documents the latest coverage figures for quick
  reference when changing core flows.
