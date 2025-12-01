Products Application
====================

The ``products`` app is the storefront-facing piece of PookieCare. It models
brands, categories, products, and lightweight ordering along with the associated
views and templates.

Homepage (``home_view``)
------------------------

* Loads in-stock products and splits them into featured (first 6) and latest 10.
* Supplies ``products`` and ``featured_products`` context variables to
  ``products/home.html`` for rendering the hero and carousel sections.

Catalog (``products_list_view``)
--------------------------------

* Filters to in-stock items and supports:

  - **Search** – ``product_name``, brand name, and category name (case-insensitive).
  - **Brand filter** – ``brand`` query parameter with UUID value.
  - **Category filter** – ``category`` query parameter with UUID value.
  - **Price range** – ``min_price``/``max_price`` query params.
  - **Sorting** – ``sort`` query parameter (``price_low``, ``price_high``,
    default latest).
* Provides ``Brand`` and ``Category`` querysets for the sidebar select widgets.

Detail Page (``product_detail_view``)
-------------------------------------

* Looks up a product by UUID and displays all attributes, including stock
  status derived from ``Product.get_stock_status()``.
* Fetches up to four related products from the same category while ensuring the
  current item is excluded.

Models Recap
------------

* ``Brand`` and ``Category`` define tidy alphabetical lists for filters.
* ``Product`` offers helper methods ``get_image_url()``, ``is_in_stock()``, and
  ``get_stock_status()`` that templates use to decide badges and asset sources.
* ``Order`` and ``OrderItem`` back the shopping cart workflow. Calling
  ``Order.complete_order()`` performs stock validation, decrements inventory per
  item, sets ``in_cart=False``, and stamps ``completed_at``.

Admin Integration
-----------------

All catalog models are registered in ``products/admin.py`` (not shown here) so
site administrators can manage brands, categories, products, and cart items via
Django admin without touching the database directly.
