"""Sphinx configuration."""
from datetime import datetime


project = "Git Portfolio"
author = "staticdev"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
linkcheck_ignore = [  # temporary workaround
    "codeofconduct.html",
    "contributing.html",
]
