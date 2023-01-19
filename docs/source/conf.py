# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
# sys.path.insert(0, os.path.abspath('../../UI'))
sys.path.insert(0, os.path.abspath('../../FileHelpers'))
sys.path.insert(0, os.path.abspath('../../Grade'))


project = 'Grading Script'
copyright = '2023 TriHard Studios'
author = 'Gregory Bell'
release = '1.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# sphinx-apidoc -o source/ ../<module>
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
]
source_suffix = [
    '.rst',
]


templates_path = ['_templates']
exclude_patterns = [
    'docs/*',
    'config/*',
    'canvas/*',
    'gradescope/*',
    'special_cases/*',
]
always_document_param_types = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# https://sphinx-themes.org/sample-sites/furo/
html_theme = 'furo'
html_static_path = []
