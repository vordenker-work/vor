import unittest
import os
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QLineEdit, QTabWidget, QScrollBar
from PyQt6.QtCore import Qt

# Ensure vor/ is in import path
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))

from core.translation.translator import Translator, language_signal
from core.translation.base_translatable_widget import BaseTranslatableWidget

class DummyTranslatableWidget(BaseTranslatableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_field = QLineEdit(self)
        self.input_field.setText("User Entered Input")
        self.retranslate_ui()

    def retranslate_ui(self):
        self.input_field.setPlaceholderText(Translator.translate("search.placeholder"))

class TestLanguageSwitchPreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        Translator.load_languages()

    def test_switch_state_preservation(self):
        # 1. Instantiate translatable widget
        widget = DummyTranslatableWidget()
        
        # 2. Check initial state
        self.assertEqual(widget.input_field.text(), "User Entered Input")
        
        # 3. Perform repeated language switching
        # Switch to Vietnamese
        Translator.set_language("vi")
        self.assertEqual(widget.input_field.placeholderText(), Translator.translate("search.placeholder"))
        self.assertEqual(widget.input_field.text(), "User Entered Input") # Input preserved
        
        # Switch to English
        Translator.set_language("en")
        self.assertEqual(widget.input_field.placeholderText(), Translator.translate("search.placeholder"))
        self.assertEqual(widget.input_field.text(), "User Entered Input") # Input preserved
        
        # 4. Clean up widget
        widget.deleteLater()

    def test_scroll_and_tab_preservation(self):
        tab_widget = QTabWidget()
        tab_widget.addTab(QLineEdit("Tab 1 Content"), "Tab 1")
        tab_widget.addTab(QLineEdit("Tab 2 Content"), "Tab 2")
        tab_widget.setCurrentIndex(1)
        
        scroll = QScrollBar(Qt.Orientation.Vertical)
        scroll.setValue(50)
        
        # Switch language
        Translator.set_language("vi")
        
        # Assert indices/values remain unchanged
        self.assertEqual(tab_widget.currentIndex(), 1)
        self.assertEqual(scroll.value(), 50)
        
        # Switch back
        Translator.set_language("en")
        self.assertEqual(tab_widget.currentIndex(), 1)
        self.assertEqual(scroll.value(), 50)
        
        tab_widget.deleteLater()
        scroll.deleteLater()

if __name__ == "__main__":
    unittest.main()
