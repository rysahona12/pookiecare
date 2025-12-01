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

Extensibility
-------------

* Additional Django apps (e.g., payments or reviews) can plug into the existing
  project by updating ``INSTALLED_APPS`` and the root ``urls.py``.
* The Sphinx documentation uses autodoc to pull live docstrings from both apps,
  so future modules become part of the API reference without extra wiring once
  they expose docstrings.
