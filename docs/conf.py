"""Sphinx configuration for pyflare documentation.

Build locally::

    pip install -e ".[docs]"
    sphinx-build -b html docs docs/_build

Open ``docs/_build/index.html`` in a browser to preview.

Hosted on Read the Docs via ``.readthedocs.yaml`` at the repo root.
"""

from __future__ import annotations

import os
import sys
from datetime import date

# Make the source package importable for autodoc.
sys.path.insert(0, os.path.abspath("../src"))


# -- Project information -----------------------------------------------------

project = "pyflare"
author = "Johnpaul Okeke"
copyright = f"{date.today().year}, {author}"

# The version reflects the installed package metadata.
import pyflare  # noqa: E402

release = pyflare.__version__
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",          # NumPy- and Google-style docstrings
    "sphinx.ext.viewcode",          # link to source from API pages
    "sphinx.ext.intersphinx",       # cross-references to numpy / pandas
    "sphinx_autodoc_typehints",     # render type hints into docstrings
    "myst_parser",                  # Markdown support alongside reST
]

# Markdown sources are treated the same as reST.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Autodoc / Napoleon — we use NumPy-style throughout pyflare.
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}


# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_title = f"pyflare {release}"
html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/Jayyp1234/pyflare",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/Jayyp1234/pyflare",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-2x",
        },
    ],
    "light_css_variables": {
        "color-brand-primary": "#d44500",
        "color-brand-content": "#d44500",
    },
    "dark_css_variables": {
        "color-brand-primary": "#ff7a3a",
        "color-brand-content": "#ff7a3a",
    },
}
