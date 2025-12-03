User Application
================

The ``user`` app provides the custom authentication core for PookieCare. It
stores customer identity information, enforces Bangladeshi contact rules, and
ships the registration/login/profile interfaces used on the site and in the
admin.

Data Model Highlights
---------------------

* ``User`` replaces Django's default ``User`` with a UUID primary key.
* Required contact fields: email (used for login), Bangladeshi phone number,
  full name, and mailing address (house, road, postal code, district, country).
* Helper methods ``get_full_name()``, ``get_short_name()``, and
  ``get_full_address()`` support consistent rendering across templates and
  emails.

Registration Workflow
---------------------

``user.views.register_view`` uses ``UserRegistrationForm`` to collect all
required profile data plus a password confirmation. Validation rules:

* Phone numbers must start with ``01`` and contain exactly 11 digits (no spaces
  or symbols).
* Email addresses must be unique across the table.
* All address fields are mandatory, ensuring shipping-ready records.

Successful submissions create a user, flash a success message, and redirect to
the login page.

Authentication & Sessions
-------------------------

* ``user.backends.EmailBackend`` allows login with email + password while still
  honoring Django's built-in backend chain.
* ``login_view`` authenticates credentials, logs the user in, and greets them
  with a personalized message before redirecting to ``user:profile``.
* ``logout_view`` is protected by ``@login_required`` and clears the session
  before redirecting to the login page.
* ``LOGIN_URL``/``LOGIN_REDIRECT_URL``/``LOGOUT_REDIRECT_URL`` are configured in
  ``pookiecare.settings`` so other views rely on the same flow.

Profile Management
------------------

``profile_view`` simply renders the authenticated user's data, while
``edit_profile_view`` relies on ``UserProfileEditForm`` to update names, phone,
and address fields. Validation mirrors the registration form to ensure
consistent formatting. Both views require authentication and use Django message
alerts to confirm updates or highlight validation issues.

Admin Experience
----------------

``user/admin.py`` defines custom ``UserAdmin`` behavior:

* Separate creation/change forms enforce password confirmation for staff-created
  accounts and lock the hashed password field on edit.
* List views expose search on email, name, and phone along with filters for
  staff status, superuser, active flag, and district.
* Fieldsets group authentication, personal info, address, permissions, and key
  timestamps while keeping ``country`` read-only.
* ``filter_horizontal`` on groups/permissions keeps the UX manageable even as
  roles grow.

Testing & Quality
-----------------

``python manage.py test user.tests`` runs the dedicated suite (37 tests in the
current repository) that covers model validation, registration rules, login
flows, profile updates, and custom backend behavior. Keep these tests green when
changing the user experience to guarantee parity between the docs and code.
