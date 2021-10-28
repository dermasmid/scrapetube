import os
import sys

sys.path.insert(0, os.path.abspath("../"))
from scrapetube import __version__ as release


project = "Scrapetube"
copyright = "2021, Cheskel Twersky"
author = "Cheskel Twersky"


extensions = ["sphinx.ext.autodoc", "sphinx.ext.coverage", "sphinx.ext.napoleon"]

templates_path = ["_templates"]


exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


html_theme = "sphinx_rtd_theme"
