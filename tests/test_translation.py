import unittest
import os
import json
import sys

# Ensure vor/ is in import path
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

from core.translation.translator import Translator

class TestTranslationSystem(unittest.TestCase):
    def setUp(self):
        Translator.load_languages()

    def test_structural_equivalence(self):
        lang_dir = Translator._lang_dir
        en_path = os.path.join(lang_dir, "en.json")
        vi_path = os.path.join(lang_dir, "vi.json")
        
        self.assertTrue(os.path.exists(en_path))
        self.assertTrue(os.path.exists(vi_path))
        
        with open(en_path, "r", encoding="utf-8") as f:
            en_trans = json.load(f).get("translations", {})
        with open(vi_path, "r", encoding="utf-8") as f:
            vi_trans = json.load(f).get("translations", {})
            
        en_keys = set(en_trans.keys())
        vi_keys = set(vi_trans.keys())
        
        self.assertEqual(en_keys, vi_keys, f"Keys mismatch. Keys in en but not vi: {en_keys - vi_keys}. Keys in vi but not en: {vi_keys - en_keys}")

    def test_parameter_interpolation(self):
        # Inject key dynamically for testing
        lang = Translator.current_language()
        if lang not in Translator._translations:
            Translator._translations[lang] = {}
        Translator._translations[lang]["test.greet"] = "Hello {name}"
        
        res = Translator.translate("test.greet", name="Henry")
        self.assertEqual(res, "Hello Henry")

    def test_plural_selection(self):
        lang = Translator.current_language()
        if lang not in Translator._translations:
            Translator._translations[lang] = {}
        Translator._translations[lang]["test.tasks.plural.one"] = "1 Task"
        Translator._translations[lang]["test.tasks.plural.other"] = "{count} Tasks"
        
        res1 = Translator.plural("test.tasks", 1)
        self.assertEqual(res1, "1 Task")
        
        res2 = Translator.plural("test.tasks", 5)
        self.assertEqual(res2, "5 Tasks")

    def test_fallback_logic(self):
        res = Translator.translate("non_existent_key_xyz", default="Fallback default")
        self.assertEqual(res, "Fallback default")

if __name__ == "__main__":
    unittest.main()
