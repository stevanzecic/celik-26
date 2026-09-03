"""JSON-backed translations for the desktop UI."""

import json
from pathlib import Path


LANGUAGES = {"sr": "Srpski", "en": "English"}
DEFAULT_LANGUAGE = "sr"
_RESOURCE_DIR = Path(__file__).with_name("translations")


def _load_catalog(language):
    path = _RESOURCE_DIR / f"{language}.json"
    try:
        with path.open(encoding="utf-8") as file:
            catalog = json.load(file)
    except (OSError, ValueError):
        catalog = {}
    return catalog if isinstance(catalog, dict) else {}


_TEXT = {language: _load_catalog(language) for language in LANGUAGES}


def tr(key, language=DEFAULT_LANGUAGE, **kwargs):
    """Return a translated string, falling back to the key when unavailable."""
    catalog = _TEXT.get(language, _TEXT[DEFAULT_LANGUAGE])
    value = catalog.get(key, key)
    return str(value).format(**kwargs)
