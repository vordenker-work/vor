# i18n.py
from core.translation.translator import Translator

def _(key, default=None, **kwargs):
    """Retrieve translated string with fallbacks and parameter support."""
    return Translator.translate(key, default, **kwargs)

def set_language(lang_code):
    """Change system display language."""
    return Translator.set_language(lang_code)
