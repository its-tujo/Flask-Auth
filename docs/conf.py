# -- Projektinformationen -----------------------------------------------------
project = 'FlaskAuth'
author = 'THE_13joker1'
release = '1.0'

# -- Allgemeine Konfiguration -------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Automatische Dokumentation aus Docstrings
    'sphinx.ext.viewcode',      # Quellcode-Links
    'sphinx.ext.napoleon',      # Unterstützung für NumPy- und Google-Stil-Dokumentation
]

templates_path = ['_templates']
exclude_patterns = []

# -- HTML-Ausgabe Optionen ----------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
