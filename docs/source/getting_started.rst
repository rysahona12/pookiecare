Getting Started
===============

Follow these steps to run PookieCare locally and build the accompanying
Sphinx documentation.

Prerequisites
-------------

* Python 3.13
* pip
* virtualenv (optional but recommended)
* SQLite (bundled with Python on most systems)

Project Setup
-------------

.. code-block:: bash

   git clone https://github.com/rysahona12/pookiecare.git
   cd pookiecare
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt

Database Migration & Superuser
------------------------------

.. code-block:: bash

   python manage.py migrate
   python manage.py createsuperuser  # provide email, phone, name, address, password

Running the Development Server
------------------------------

.. code-block:: bash

   python manage.py runserver

Key URLs while developing:

* ``/`` – Landing page featuring highlighted and latest products.
* ``/products/`` – Full catalog with search, brand/category filters, and price sorting.
* ``/user/register/`` – Customer registration that collects contact + address fields.
* ``/user/login/`` – Email-based authentication.
* ``/user/profile/`` – Profile dashboard for logged-in users.
* ``/admin/`` – Django admin for managing users, brands, categories, products, and orders.

Running Tests
-------------

.. code-block:: bash

   python manage.py test                # run all tests (user + products)
   python manage.py test user.tests     # run user app tests only
   python manage.py test products.tests # run products app tests only

Building This Documentation
---------------------------

Install the Sphinx requirement and build the HTML output:

.. code-block:: bash

   pip install -r docs/requirements.txt
   cd docs
   make html    # Windows: .\make.bat html

Open ``docs/build/html/index.html`` in your browser to view the rendered site.
