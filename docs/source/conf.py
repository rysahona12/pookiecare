"""Sphinx configuration for the PookieCare project documentation."""
from __future__ import annotations

import os
import sys

import django

# Add project root to sys.path so autodoc can import Django apps
sys.path.insert(0, os.path.abspath('../..'))

# Configure Django so autodoc can introspect models/views
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pookiecare.settings')
django.setup()

project = 'PookieCare'
copyright = '2025, PookieCare Team'
author = 'PookieCare Team'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns: list[str] = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
