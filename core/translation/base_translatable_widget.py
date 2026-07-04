from PyQt6.QtWidgets import QWidget, QFrame, QDialog
from core.translation.translator import language_signal

def make_translatable(widget, key, default=None):
    widget.translation_key = key
    from core.translation.translator import Translator
    if hasattr(widget, "setText"):
        try: widget.setText(Translator.translate(key, default))
        except Exception: pass
    elif hasattr(widget, "setPlaceholderText"):
        try: widget.setPlaceholderText(Translator.translate(key, default))
        except Exception: pass
    return widget

class BaseTranslatableWidget(QWidget):
    """Base QWidget subclass that auto-registers and auto-cleans translation signals."""
    def __init__(self, parent=None):
        super().__init__(parent)
        language_signal.language_changed.connect(self.safe_retranslate_ui)
        self.destroyed.connect(self._cleanup_translation)

    def safe_retranslate_ui(self):
        try:
            self.retranslate_ui()
        except Exception as e:
            print(f"Error in retranslate_ui for {self.__class__.__name__}: {e}")

    def _cleanup_translation(self):
        try:
            language_signal.language_changed.disconnect(self.safe_retranslate_ui)
        except Exception:
            pass

    def retranslate_ui(self):
        # 1. Update this widget's own properties
        from core.translation.translator import Translator
        if hasattr(self, "translation_key") and hasattr(self, "setText"):
            try: self.setText(Translator.translate(self.translation_key))
            except Exception: pass
        if hasattr(self, "placeholder_translation_key") and hasattr(self, "setPlaceholderText"):
            try: self.setPlaceholderText(Translator.translate(self.placeholder_translation_key))
            except Exception: pass
        if hasattr(self, "tooltip_translation_key") and hasattr(self, "setToolTip"):
            try: self.setToolTip(Translator.translate(self.tooltip_translation_key))
            except Exception: pass
        if hasattr(self, "window_title_translation_key") and hasattr(self, "setWindowTitle"):
            try: self.setWindowTitle(Translator.translate(self.window_title_translation_key))
            except Exception: pass

        # 2. Update all child widgets recursively
        for child in self.findChildren(QWidget):
            if hasattr(child, "translation_key") and hasattr(child, "setText"):
                try: child.setText(Translator.translate(child.translation_key))
                except Exception: pass
            if hasattr(child, "placeholder_translation_key") and hasattr(child, "setPlaceholderText"):
                try: child.setPlaceholderText(Translator.translate(child.placeholder_translation_key))
                except Exception: pass
            if hasattr(child, "tooltip_translation_key") and hasattr(child, "setToolTip"):
                try: child.setToolTip(Translator.translate(child.tooltip_translation_key))
                except Exception: pass
            if hasattr(child, "window_title_translation_key") and hasattr(child, "setWindowTitle"):
                try: child.setWindowTitle(Translator.translate(child.window_title_translation_key))
                except Exception: pass


class BaseTranslatableFrame(QFrame):
    """Base QFrame subclass that auto-registers and auto-cleans translation signals."""
    def __init__(self, parent=None):
        super().__init__(parent)
        language_signal.language_changed.connect(self.safe_retranslate_ui)
        self.destroyed.connect(self._cleanup_translation)

    def safe_retranslate_ui(self):
        try:
            self.retranslate_ui()
        except Exception as e:
            print(f"Error in retranslate_ui for {self.__class__.__name__}: {e}")

    def _cleanup_translation(self):
        try:
            language_signal.language_changed.disconnect(self.safe_retranslate_ui)
        except Exception:
            pass

    def retranslate_ui(self):
        # 1. Update this widget's own properties
        from core.translation.translator import Translator
        if hasattr(self, "translation_key") and hasattr(self, "setText"):
            try: self.setText(Translator.translate(self.translation_key))
            except Exception: pass
        if hasattr(self, "placeholder_translation_key") and hasattr(self, "setPlaceholderText"):
            try: self.setPlaceholderText(Translator.translate(self.placeholder_translation_key))
            except Exception: pass
        if hasattr(self, "tooltip_translation_key") and hasattr(self, "setToolTip"):
            try: self.setToolTip(Translator.translate(self.tooltip_translation_key))
            except Exception: pass
        if hasattr(self, "window_title_translation_key") and hasattr(self, "setWindowTitle"):
            try: self.setWindowTitle(Translator.translate(self.window_title_translation_key))
            except Exception: pass

        # 2. Update all child widgets recursively
        for child in self.findChildren(QWidget):
            if hasattr(child, "translation_key") and hasattr(child, "setText"):
                try: child.setText(Translator.translate(child.translation_key))
                except Exception: pass
            if hasattr(child, "placeholder_translation_key") and hasattr(child, "setPlaceholderText"):
                try: child.setPlaceholderText(Translator.translate(child.placeholder_translation_key))
                except Exception: pass
            if hasattr(child, "tooltip_translation_key") and hasattr(child, "setToolTip"):
                try: child.setToolTip(Translator.translate(child.tooltip_translation_key))
                except Exception: pass
            if hasattr(child, "window_title_translation_key") and hasattr(child, "setWindowTitle"):
                try: child.setWindowTitle(Translator.translate(child.window_title_translation_key))
                except Exception: pass


class BaseTranslatableDialog(QDialog):
    """Base QDialog subclass that auto-registers and auto-cleans translation signals."""
    def __init__(self, parent=None):
        super().__init__(parent)
        language_signal.language_changed.connect(self.safe_retranslate_ui)
        self.destroyed.connect(self._cleanup_translation)

    def safe_retranslate_ui(self):
        try:
            self.retranslate_ui()
        except Exception as e:
            print(f"Error in retranslate_ui for {self.__class__.__name__}: {e}")

    def _cleanup_translation(self):
        try:
            language_signal.language_changed.disconnect(self.safe_retranslate_ui)
        except Exception:
            pass

    def retranslate_ui(self):
        # 1. Update this widget's own properties
        from core.translation.translator import Translator
        if hasattr(self, "translation_key") and hasattr(self, "setText"):
            try: self.setText(Translator.translate(self.translation_key))
            except Exception: pass
        if hasattr(self, "placeholder_translation_key") and hasattr(self, "setPlaceholderText"):
            try: self.setPlaceholderText(Translator.translate(self.placeholder_translation_key))
            except Exception: pass
        if hasattr(self, "tooltip_translation_key") and hasattr(self, "setToolTip"):
            try: self.setToolTip(Translator.translate(self.tooltip_translation_key))
            except Exception: pass
        if hasattr(self, "window_title_translation_key") and hasattr(self, "setWindowTitle"):
            try: self.setWindowTitle(Translator.translate(self.window_title_translation_key))
            except Exception: pass

        # 2. Update all child widgets recursively
        for child in self.findChildren(QWidget):
            if hasattr(child, "translation_key") and hasattr(child, "setText"):
                try: child.setText(Translator.translate(child.translation_key))
                except Exception: pass
            if hasattr(child, "placeholder_translation_key") and hasattr(child, "setPlaceholderText"):
                try: child.setPlaceholderText(Translator.translate(child.placeholder_translation_key))
                except Exception: pass
            if hasattr(child, "tooltip_translation_key") and hasattr(child, "setToolTip"):
                try: child.setToolTip(Translator.translate(child.tooltip_translation_key))
                except Exception: pass
            if hasattr(child, "window_title_translation_key") and hasattr(child, "setWindowTitle"):
                try: child.setWindowTitle(Translator.translate(child.window_title_translation_key))
                except Exception: pass
