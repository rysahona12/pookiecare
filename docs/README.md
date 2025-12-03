# PookieCare Documentation Guide

This project uses [Sphinx](https://www.sphinx-doc.org/) to publish developer
documentation from the `docs/` directory. Use this guide to extend or refresh
the docs without guesswork.

## Folder Layout

```
docs/
├── Makefile / make.bat  # platform-specific build helpers
├── requirements.txt     # Sphinx + theme dependencies
├── source/              # ReStructuredText (.rst) sources
│   ├── conf.py          # Sphinx configuration (autodoc, theme, paths)
│   ├── index.rst        # Root table of contents
│   ├── getting_started.rst
│   ├── architecture.rst
│   ├── products_app.rst
│   ├── api_reference.rst
│   ├── _static/         # custom CSS/JS assets
│   └── _templates/      # custom Jinja templates
└── build/               # Generated output (ignored in git)
```

## Prerequisites

Create or activate the Python environment used for the Django project and
install the Sphinx requirements:

```bash
pip install -r docs/requirements.txt
```

## Building Locally

```bash
cd docs
make html          # Linux/macOS
# or
.\make.bat html    # Windows PowerShell / CMD
```

Results land in `docs/build/html/index.html`. Use `make clean html` to force a
full rebuild when you add new extensions or files.

## Adding Pages

1. Create a new `.rst` file in `docs/source/`.
2. Reference the file from `index.rst` (or another parent page) via
   `.. toctree::` so it shows up in navigation.
3. Rebuild with `make html` and confirm the new page renders correctly.

Keep page content grounded in implemented features to avoid misleading future
readers.

## Autodoc Reference

The `conf.py` file bootstraps Django so `autodoc` can import real modules. To
expose new modules/classes/functions:

```rst
.. automodule:: path.to.module
   :members:
   :undoc-members:
```

If the module depends on additional third-party packages, ensure they are
installed in the active environment before building docs.

## Theming & Custom Assets

Sphinx currently uses the Read-the-Docs theme. You can tweak the appearance by
adding CSS files inside `_static/` and referencing them via `html_css_files` in
`conf.py`, or by switching `html_theme`. Template overrides should live inside
`_templates/`.

## Common Tasks Checklist

- **Update content:** edit the relevant `.rst` file and re-run `make html`.
- **Add screenshots/assets:** drop them into `_static/` and embed using the
  `.. image::` directive.
- **Change theme/extensions:** update `docs/requirements.txt`, adjust `conf.py`,
  reinstall requirements, and rebuild.
- **Troubleshoot Windows builds:** ensure `_static/` and `_templates/` folders
  exist (Git keeps them via `.gitkeep`) and run `.\make.bat clean html`.

Following this workflow keeps the documentation consistent and makes it easy for
future contributors to extend the guide alongside the codebase.
