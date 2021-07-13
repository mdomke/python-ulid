import os
import sys


sys.path.insert(0, os.path.abspath(".."))

project = ""
copyright = "2020, Martin Domke"
author = "Martin Domke"
master_doc = "index"
source_suffix = [".rst", ".md"]

# The full version, including alpha/beta/rc tags
release = "1.0.0"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_logo = "../logo.png"
html_theme = "alabaster"
html_theme_options = {
    "github_user": "mdomke",
    "github_repo": "python-ulid",
    "description": "A library for working with ULIDs",
    "sidebar_collapse": False,
    "logo_text_align": "center",
}
html_sidebars = {
    "**": ["about.html", "navigation.html", "relations.html", "searchbox.html", "donate.html"]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
pygments_style = "sphinx"
