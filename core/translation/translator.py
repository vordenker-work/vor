import os
import json
from PyQt6.QtCore import QObject, pyqtSignal, QLocale
from modules.local_storage import local_data

class LanguageSignal(QObject):
    language_changed = pyqtSignal(str)

language_signal = LanguageSignal()

class Translator:
    _current_lang = "vi"
    _translations = {}
    _lang_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "languages"))
    _missing_keys = set()
    _unused_keys = set()

    @classmethod
    def load_languages(cls):
        """Loads all translation files once and caches them in memory."""
        if not os.path.exists(cls._lang_dir):
            os.makedirs(cls._lang_dir, exist_ok=True)
            
        cls._translations = {}
        for filename in os.listdir(cls._lang_dir):
            if filename.endswith(".json"):
                lang_code = filename[:-5]
                filepath = os.path.join(cls._lang_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Read according to the enterprise JSON schema structure
                        if isinstance(data, dict) and "translations" in data:
                            cls._translations[lang_code] = data["translations"]
                        else:
                            cls._translations[lang_code] = data
                except Exception as e:
                    print(f"Error loading language file {filename}: {e}")

        # Retrieve stored language selection
        cls._current_lang = local_data.get("language", "vi")
        cls._sync_qt_locale()

    @classmethod
    def _sync_qt_locale(cls):
        """Synchronizes the Qt default locale with the current language settings."""
        if cls._current_lang == "vi":
            QLocale.setDefault(QLocale(QLocale.Language.Vietnamese, QLocale.Country.Vietnam))
        else:
            QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

    @classmethod
    def translate(cls, key, default=None, **kwargs):
        """Translates the key, interpolating parameters and handling missing/fallbacks."""
        if not cls._translations:
            cls.load_languages()

        lang_dict = cls._translations.get(cls._current_lang, {})
        val = lang_dict.get(key)

        if val is None:
            # Log missing translation key
            cls._missing_keys.add((key, cls._current_lang))
            print(f"Missing Translation: key='{key}', lang='{cls._current_lang}'")
            cls._generate_report()

            # Fallback to English
            en_dict = cls._translations.get("en", {})
            val = en_dict.get(key)

            if val is None:
                # Fallback to key itself
                val = default if default is not None else key

        # Support runtime parameterized interpolations
        if kwargs and isinstance(val, str):
            try:
                val = val.format(**kwargs)
            except Exception as e:
                print(f"Translation interpolation error for key '{key}': {e}")
        
        return val

    @classmethod
    def plural(cls, key, count, **kwargs):
        """Selects singular or plural based on counts using VKU/standard standards."""
        # For Vietnamese, there's usually no morphological plural distinction,
        # but we support different plural forms via key suffix mapping.
        # Format keys: key.plural.one and key.plural.other
        suffix = "one" if count == 1 else "other"
        plural_key = f"{key}.plural.{suffix}"
        
        # Check if the specific plural key exists, otherwise fallback to standard key
        translations = cls._translations.get(cls._current_lang, {})
        if plural_key in translations:
            return cls.translate(plural_key, count=count, **kwargs)
            
        # Fallback to standard key
        return cls.translate(key, count=count, **kwargs)

    @classmethod
    def set_language(cls, lang_code):
        """Updates display language dynamically and notifies all translatable widgets."""
        if lang_code in cls.available_languages():
            cls._current_lang = lang_code
            local_data.save("language", lang_code)
            local_data.save_to_disk()
            cls._sync_qt_locale()
            # Emit notification to update all visible UI components
            language_signal.language_changed.emit(lang_code)
            return True
        return False

    @classmethod
    def current_language(cls):
        return cls._current_lang

    @classmethod
    def available_languages(cls):
        if not cls._translations:
            cls.load_languages()
        return list(cls._translations.keys())

    @classmethod
    def reload(cls):
        """Forces reload of all JSON strings and updates currently running windows."""
        cls.load_languages()
        language_signal.language_changed.emit(cls._current_lang)

    @classmethod
    def register_plugin_translations(cls, lang_code, translations_dict):
        """Allows dynamically loaded modules to inject translations at runtime."""
        if lang_code not in cls._translations:
            cls._translations[lang_code] = {}
        cls._translations[lang_code].update(translations_dict)

    @classmethod
    def _generate_report(cls):
        """Generates translation_report.txt report listing missing keys."""
        report_path = os.path.normpath(os.path.join(cls._lang_dir, "..", "..", "..", "translation_report.txt"))
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("=== Missing Translation Keys ===\n")
                for key, lang in sorted(cls._missing_keys):
                    f.write(f"Lang: {lang} | Key: {key}\n")
        except Exception as e:
            print(f"Error writing translation report: {e}")
