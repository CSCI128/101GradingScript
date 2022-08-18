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


project = '101GradingScript'
copyright = '2022, Gregory Bell'
author = 'Gregory Bell'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# sphinx-apidoc -o source/ ../<module>
extensions = [
    'sphinx_markdown_builder',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'myst_parser',
]
source_suffix = [
    '.rst',
    '.md'
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

html_theme = 'alabaster'
html_static_path = ['_static']