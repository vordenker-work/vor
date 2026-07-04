from core.translation.base_translatable_widget import make_translatable
from core.translation.base_translatable_widget import BaseTranslatableWidget, BaseTranslatableFrame, BaseTranslatableDialog
from core.translation.translator import Translator
import sys
import datetime
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QTextEdit, QScrollArea, QFrame, QGridLayout, 
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QApplication, QCalendarWidget,
    QCheckBox, QSizePolicy, QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QPoint, QRect, QSize, QEvent
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QCursor, QMouseEvent, QKeyEvent

# Dialog Manager for stack coordination
class DialogManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DialogManager, cls).__new__(cls)
            cls._instance.active_dialogs = []
        return cls._instance
        
    def register(self, dialog):
        if dialog not in self.active_dialogs:
            self.active_dialogs.append(dialog)
            
    def unregister(self, dialog):
        if dialog in self.active_dialogs:
            self.active_dialogs.remove(dialog)

dialog_manager = DialogManager()

class BaseDialog(BaseTranslatableDialog):
    def __init__(self, parent=None, size_class="medium", click_position=None):
        self._card_scale = 0.95  # Initialize first to avoid animation system getter AttributeError
        super().__init__(parent)
        dialog_manager.register(self)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.click_position = click_position
        
        # Dimensions based on size class
        self.widths = {
            "small": 400,
            "medium": 520,
            "large": 740,
            "extra": 960
        }
        self.heights = {
            "small": 260,
            "medium": 460,
            "large": 620,
            "extra": 740
        }
        self.dialog_width = self.widths.get(size_class, 640)
        self.dialog_height = self.heights.get(size_class, 550)
        
        # Find active/main window for parenting overlay
        self.parent_window = parent.window() if parent else QApplication.activeWindow()
        if self.parent_window:
            self.parent_window.installEventFilter(self)
            
        # The main card widget (white dialog card)
        self.card = QFrame(self)
        self.card.setObjectName("DialogCard")
        self.card.setStyleSheet("""
            #DialogCard {
                background-color: #FFFFFF;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        # Large soft shadow
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(15, 23, 42, 30))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)
        
        # Card layout
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)
        
        # Fade & scale animation properties
        self.opacity_effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(self.opacity_effect)
        
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.scale_anim = QPropertyAnimation(self, b"card_scale")
        
        self.overlay_color = QColor(0, 0, 0, 0) # Completely transparent overlay to keep view clean white
        self.is_closing = False
        
        # Initial sizing
        self.update_geometry()
        
    @pyqtProperty(float)
    def card_scale(self):
        return self._card_scale
        
    @card_scale.setter
    def card_scale(self, val):
        self._card_scale = val
        self.update_card_geometry()
        
    def update_geometry(self):
        if self.parent_window and self.parent_window.isVisible():
            self.setGeometry(self.parent_window.geometry())
        else:
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
                
    def update_card_geometry(self):
        w = min(self.dialog_width, self.width() - 40)
        h = min(self.dialog_height, self.height() - 40)
        
        scaled_w = int(w * self._card_scale)
        scaled_h = int(h * self._card_scale)
        
        if hasattr(self, 'click_position') and self.click_position:
            local_pos = self.mapFromGlobal(self.click_position)
            x = local_pos.x()
            y = local_pos.y()
            
            # Boundary check
            if x + scaled_w > self.width():
                x = self.width() - scaled_w - 20
            if y + scaled_h > self.height():
                y = self.height() - scaled_h - 20
            if x < 20:
                x = 20
            if y < 20:
                y = 20
        else:
            x = (self.width() - scaled_w) // 2
            y = (self.height() - scaled_h) // 2
            
        self.card.setGeometry(x, y, scaled_w, scaled_h)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_geometry()
        
    def eventFilter(self, obj, event):
        if obj == self.parent_window and event.type() in (QEvent.Type.Resize, QEvent.Type.Move):
            self.update_geometry()
        return super().eventFilter(obj, event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.overlay_color)
        
    def showEvent(self, event):
        self.update_geometry()
        self._card_scale = 0.95
        self.setWindowOpacity(0.0)
        self.update_card_geometry()
        
        self.fade_anim.stop()
        self.fade_anim.setTargetObject(self)
        self.fade_anim.setPropertyName(b"windowOpacity")
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setDuration(200)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.scale_anim.stop()
        self.scale_anim.setTargetObject(self)
        self.scale_anim.setPropertyName(b"card_scale")
        self.scale_anim.setStartValue(0.95)
        self.scale_anim.setEndValue(1.0)
        self.scale_anim.setDuration(200)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        
        self.fade_anim.start()
        self.scale_anim.start()
        super().showEvent(event)
        
    def animate_close(self, result_code):
        if self.is_closing:
            return
        self.is_closing = True
        self.result_code = result_code
        
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setDuration(150)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.scale_anim.stop()
        self.scale_anim.setStartValue(self._card_scale)
        self.scale_anim.setEndValue(0.95)
        self.scale_anim.setDuration(150)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.fade_anim.finished.connect(self._on_close_finished)
        self.fade_anim.start()
        self.scale_anim.start()
        
    def _on_close_finished(self):
        self.fade_anim.finished.disconnect(self._on_close_finished)
        dialog_manager.unregister(self)
        super().done(self.result_code)
        
    def accept(self):
        self.animate_close(QDialog.DialogCode.Accepted)
        
    def reject(self):
        self.animate_close(QDialog.DialogCode.Rejected)
        
    def done(self, r):
        if self.is_closing:
            super().done(r)
        else:
            self.animate_close(r)
            
    def mousePressEvent(self, event: QMouseEvent):
        if not self.card.geometry().contains(event.pos()):
            self.reject()
        else:
            super().mousePressEvent(event)
            
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            focused = self.focusWidget()
            if isinstance(focused, QTextEdit):
                super().keyPressEvent(event)
            else:
                self.accept()
        else:
            super().keyPressEvent(event)

# Dialog Components
class DialogHeader(BaseTranslatableWidget):
    close_clicked = pyqtSignal()
    more_clicked = pyqtSignal()
    pin_clicked = pyqtSignal()
    
    def __init__(self, title, icon_char="🗓️", has_more=True, has_pin=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #F1F5F9;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)
        
        # Left Icon
        self.icon_lbl = QLabel(icon_char)
        self.icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
        layout.addWidget(self.icon_lbl)
        
        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A; font-family: 'Inter', sans-serif;")
        layout.addWidget(self.title_lbl)
        layout.addStretch()
        
        btn_style = """
            QPushButton {
                background: transparent;
                color: #64748B;
                border-radius: 6px;
                font-size: 16px;
                padding: 4px;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """
        
        if has_pin:
            self.pin_btn = make_translatable(QPushButton(), "dialog.str_2")
            self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.pin_btn.setStyleSheet(btn_style)
            self.pin_btn.clicked.connect(self.pin_clicked)
            layout.addWidget(self.pin_btn)
            
        if has_more:
            self.more_btn = make_translatable(QPushButton(), "ui.str_10")
            self.more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.more_btn.setStyleSheet(btn_style)
            self.more_btn.clicked.connect(self.more_clicked)
            layout.addWidget(self.more_btn)
            
        self.close_btn = QPushButton("✕")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(btn_style + " QPushButton:hover { color: #EF4444; }")
        self.close_btn.clicked.connect(self.close_clicked)
        layout.addWidget(self.close_btn)

class DialogBody(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setStyleSheet("QScrollArea { background-color: #FFFFFF; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFFFFF;")
        self.body_layout = QVBoxLayout(self.container)
        self.body_layout.setContentsMargins(24, 24, 24, 24)
        self.body_layout.setSpacing(24) # Spacing of 24px between sections
        
        self.setWidget(self.container)
        
    def add_section(self, section_widget):
        self.body_layout.addWidget(section_widget)
        
    def add_stretch(self):
        self.body_layout.addStretch()

class DialogFooter(BaseTranslatableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("background-color: #F8FAFC; border-top: 1px solid #E2E8F0; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 0, 24, 0)
        self.layout.setSpacing(12)
        
    def add_widget_left(self, widget):
        self.layout.addWidget(widget)
        
    def add_stretch(self):
        self.layout.addStretch()
        
    def add_button(self, btn):
        self.layout.addWidget(btn)

class DialogSection(BaseTranslatableWidget):
    def __init__(self, icon_char=" ", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Left Icon
        self.icon_lbl = QLabel(icon_char)
        self.icon_lbl.setFixedWidth(24)
        self.icon_lbl.setStyleSheet("font-size: 16px; color: #64748B; background: transparent; border: none;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.icon_lbl)
        
        # Right fields layout
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(12)
        layout.addWidget(self.fields_container, 1)
        
    def add_field(self, field_widget):
        self.fields_layout.addWidget(field_widget)
        
    def add_layout(self, sub_layout):
        self.fields_layout.addLayout(sub_layout)

class DialogField(BaseTranslatableWidget):
    def __init__(self, input_widget, label_text="", parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.label_text = label_text
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        if label_text:
            self.label = QLabel(label_text)
            self.label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600; font-family: 'Inter', sans-serif;")
            self.layout.addWidget(self.label)
            
        self.layout.addWidget(self.input_widget)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: 500; font-family: 'Inter', sans-serif;")
        self.error_label.setVisible(False)
        self.layout.addWidget(self.error_label)
        
        self.setup_input_styles()
        
    def setup_input_styles(self):
        style = """
            QLineEdit, QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px 14px;
                color: #0F172A;
                font-family: "Inter", sans-serif;
                font-size: 14px;
            }
            QLineEdit:hover, QTextEdit:hover {
                border: 1px solid #CBD5E1;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #2563EB;
            }
            QLineEdit:disabled, QTextEdit:disabled {
                background-color: #F1F5F9;
                color: #94A3B8;
                border: 1px solid #E2E8F0;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 8px 12px;
                color: #0F172A;
                font-family: "Inter", sans-serif;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #CBD5E1;
            }
            QComboBox:focus {
                border: 1px solid #2563EB;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #64748B;
                width: 0;
                height: 0;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                selection-background-color: #F1F5F9;
                selection-color: #0F172A;
                color: #0F172A;
                padding: 4px;
            }
        """
        self.input_widget.setStyleSheet(style)
        
    def set_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        # Red border
        border_style = """
            border: 1px solid #EF4444 !important;
            border-radius: 8px;
            background-color: #FFFFFF;
            padding: 8px 12px;
        """
        self.input_widget.setStyleSheet(self.input_widget.styleSheet() + f" QLineEdit, QTextEdit, QComboBox {{ {border_style} }}")
        
    def clear_error(self):
        self.error_label.setVisible(False)
        self.setup_input_styles()

# Floating Picker Popups (WindowType.Popup)
def show_popup_below(button, popup_dialog):
    popup_dialog.show()
    global_pos = button.mapToGlobal(QPoint(0, button.height()))
    screen_rect = QApplication.primaryScreen().geometry()
    popup_size = popup_dialog.sizeHint()
    
    x = global_pos.x()
    y = global_pos.y()
    
    if x + popup_size.width() > screen_rect.right():
        x = screen_rect.right() - popup_size.width() - 10
    if y + popup_size.height() > screen_rect.bottom():
        y = global_pos.y() - button.height() - popup_size.height()
        
    popup_dialog.move(x, y)
    popup_dialog.exec()

class DatePickerDialog(BaseTranslatableDialog):
    date_selected = pyqtSignal(datetime.date)
    
    def __init__(self, initial_date=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(15, 23, 42, 20))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        
        header = QHBoxLayout()
        title_lbl = make_translatable(QLabel(), "dialog.select_date")
        title_lbl.setStyleSheet("font-weight: 700; color: #0F172A; font-size: 13px; border: none; background: transparent;")
        header.addWidget(title_lbl)
        header.addStretch()
        
        today_btn = make_translatable(QPushButton(), "calendar.today")
        today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #2563EB;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        header.addWidget(today_btn)
        layout.addLayout(header)
        
        self.cal = QCalendarWidget()
        self.cal.setGridVisible(False)
        self.cal.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        self.cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        
        self.cal.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #0F172A;
                background-color: #FFFFFF;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                border-radius: 6px;
                font-size: 12px;
            }
            QCalendarWidget QToolButton {
                color: #0F172A;
                background-color: #FFFFFF;
                border: none;
                font-weight: bold;
                font-size: 12px;
                border-radius: 4px;
                padding: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #F1F5F9;
            }
        """)
        
        if initial_date:
            from PyQt6.QtCore import QDate
            self.cal.setSelectedDate(QDate(initial_date.year, initial_date.month, initial_date.day))
            
        layout.addWidget(self.cal)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(frame)
        
        self.cal.clicked.connect(self._on_date_clicked)
        today_btn.clicked.connect(self._on_today_clicked)
        
    def _on_date_clicked(self, qdate):
        dt = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.date_selected.emit(dt)
        self.accept()
        
    def _on_today_clicked(self):
        from PyQt6.QtCore import QDate
        today = QDate.currentDate()
        self.cal.setSelectedDate(today)
        self._on_date_clicked(today)

class TimePickerDialog(BaseTranslatableDialog):
    period_selected = pyqtSignal(int)
    
    def __init__(self, initial_period=1, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(240)
        
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(15, 23, 42, 20))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        title_lbl = make_translatable(QLabel(), "dialog.select_period")
        title_lbl.setStyleSheet("font-weight: 700; color: #0F172A; font-size: 12px; margin: 8px 4px 4px 4px; border: none;")
        layout.addWidget(title_lbl)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setFixedHeight(250)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(4)
        
        self.periods_times = [
            (h, f"{h:02d}:00 - {h+1:02d}:00") for h in range(0, 24)
        ]
        
        for p, time_str in self.periods_times:
            btn = QPushButton(time_str)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if p == initial_period:
                btn_style = """
                    QPushButton {
                        background-color: #2563EB;
                        color: white;
                        text-align: left;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-weight: 600;
                        font-size: 12px;
                        border: none;
                    }
                """
            else:
                btn_style = """
                    QPushButton {
                        background-color: transparent;
                        color: #0F172A;
                        text-align: left;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 12px;
                        font-weight: 500;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #F1F5F9;
                    }
                """
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda checked, p_val=p: self._on_selected(p_val))
            c_layout.addWidget(btn)
            
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(frame)
        
    def _on_selected(self, p):
        self.period_selected.emit(p)
        self.accept()

class ColorPickerDialog(BaseTranslatableDialog):
    color_selected = pyqtSignal(str)
    
    def __init__(self, initial_color_type="class", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(200)
        
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(15, 23, 42, 20))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        title_lbl = make_translatable(QLabel(), "dialog.select_color_category")
        title_lbl.setStyleSheet("font-weight: 700; color: #0F172A; font-size: 12px; border: none;")
        layout.addWidget(title_lbl)
        
        grid = QGridLayout()
        grid.setSpacing(6)
        
        colors = {
            "class": ("#0284C7", "Class (Blue)"),
            "makeup": ("#A16207", "Makeup (Yellow)"),
            "self_study": ("#7E22CE", "Self Study (Purple)"),
            "exam": ("#B91C1C", "Exam (Red)"),
            "study_task": ("#15803D", "Study Task (Green)"),
            "other": ("#475569", "Other (Gray)")
        }
        
        row, col = 0, 0
        for name, (hex_val, label) in colors.items():
            btn = QPushButton()
            btn.setFixedSize(36, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if name == initial_color_type:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_val};
                        border: 3px solid #2563EB;
                        border-radius: 18px;
                        padding: 0px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_val};
                        border: 1px solid #CBD5E1;
                        border-radius: 18px;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #0F172A;
                    }}
                """)
            
            btn.setToolTip(label)
            btn.clicked.connect(lambda checked, n_val=name: self._on_selected(n_val))
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        layout.addLayout(grid)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(frame)
        
    def _on_selected(self, name):
        self.color_selected.emit(name)
        self.accept()

# Event Dialog implementations
class QuickCreateDialog(BaseDialog):
    def __init__(self, data=None, is_ai=False, click_position=None, parent=None):
        super().__init__(parent, size_class="medium", click_position=click_position)
        self.data = data
        self.is_ai = is_ai
        self.action = "cancel"
        
        self.is_edit = data is not None and data.get("title", "") != ""
        
        # Close Button at the top right inside the card
        close_lay = QHBoxLayout()
        close_lay.setContentsMargins(0, 12, 16, 0)
        close_lay.addStretch()
        self.close_btn = QPushButton("✕")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748B;
                border-radius: 6px;
                font-size: 16px;
                min-width: 28px; max-width: 28px;
                min-height: 28px; max-height: 28px;
                border: none;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #EF4444;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        close_lay.addWidget(self.close_btn)
        self.card_layout.addLayout(close_lay)
        
        # Body Scroll Area
        self.body = DialogBody(self)
        self.body.body_layout.setContentsMargins(20, 0, 20, 8)
        self.body.body_layout.setSpacing(10)
        
        # 1. Title Input (Borderless bottom underlined)
        self.title_le = QLineEdit()
        self.title_le.setPlaceholderText(Translator.translate("placeholder.add_title")); self.title_le.placeholder_translation_key = "placeholder.add_title"
        self.title_le.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: 500;
                border: none;
                border-bottom: 1px solid #CBD5E1;
                padding: 2px 0px;
                background: transparent;
                color: #0F172A;
                font-family: 'Inter', sans-serif;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2563EB;
            }
        """)
        self.title_field = DialogField(self.title_le)
        title_sec = DialogSection(" ")
        title_sec.add_field(self.title_field)
        self.body.add_section(title_sec)
        
        # 2. Type Tab Selectors: Event / Task / Appointment
        tabs_sec = DialogSection(" ")
        tabs_lay = QHBoxLayout()
        tabs_lay.setSpacing(8)
        
        self.event_tab = make_translatable(QPushButton(), "dialog.event")
        self.task_tab = make_translatable(QPushButton(), "dialog.task")
        self.appt_tab = make_translatable(QPushButton(), "dialog.appointment_schedule")
        
        for tab in (self.event_tab, self.task_tab, self.appt_tab):
            tab.setCursor(Qt.CursorShape.PointingHandCursor)
            tab.setFixedHeight(28)
            tab.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 14px;
                    padding: 0px 10px;
                    font-size: 11px;
                }
            """)
            
        self.event_tab.clicked.connect(lambda: self.select_tab("class"))
        self.task_tab.clicked.connect(lambda: self.select_tab("study_task"))
        self.appt_tab.clicked.connect(lambda: self.select_tab("other"))
        
        tabs_lay.addWidget(self.event_tab)
        tabs_lay.addWidget(self.task_tab)
        tabs_lay.addWidget(self.appt_tab)
        tabs_lay.addStretch()
        tabs_sec.add_layout(tabs_lay)
        self.body.add_section(tabs_sec)
        
        # Default category/type selection
        self.selected_type = "study_task" if is_ai else "class"
        if data and data.get("type"):
            self.selected_type = data.get("type")
        self.select_tab(self.selected_type)
        
        # 3. Date & Time Row (🕒)
        self.time_sec = DialogSection("🕒")
        
        dt_vbox = QVBoxLayout()
        dt_vbox.setSpacing(4)
        
        dt_hbox = QHBoxLayout()
        dt_hbox.setSpacing(8)
        
        # Day Button (displays dynamically formatted date like "Sunday, June 28")
        self.date_btn = make_translatable(QPushButton(), "dialog.select_day")
        self.date_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.date_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0F172A;
                font-weight: 500;
                font-size: 12px;
                border: none;
                padding: 2px 0px;
                text-align: left;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        self.selected_day = "Monday"
        self.date_btn.clicked.connect(self.choose_date)
        dt_hbox.addWidget(self.date_btn)
        
        # Period start/end or duration button
        self.start_p_btn = make_translatable(QPushButton(), "ui.period_1")
        self.start_p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_p_btn.setStyleSheet(self.date_btn.styleSheet())
        self.selected_start_period = 1
        self.start_p_btn.clicked.connect(self.choose_start_period)
        dt_hbox.addWidget(self.start_p_btn)
        
        self.to_lbl = make_translatable(QLabel(), "dialog.str_3")
        self.to_lbl.setStyleSheet("color: #64748B; font-weight: 500; font-size: 14px; border: none;")
        dt_hbox.addWidget(self.to_lbl)
        
        self.end_p_btn = make_translatable(QPushButton(), "ui.period_1")
        self.end_p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_p_btn.setStyleSheet(self.date_btn.styleSheet())
        self.selected_end_period = 1
        self.end_p_btn.clicked.connect(self.choose_end_period)
        dt_hbox.addWidget(self.end_p_btn)
        dt_hbox.addStretch()
        dt_vbox.addLayout(dt_hbox)
        
        # Repeat settings label
        self.repeat_btn = make_translatable(QPushButton(), "dialog.does_not_repeat")
        self.repeat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repeat_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748B;
                font-size: 12px;
                border: none;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #2563EB;
            }
        """)
        self.selected_repeat = "Does not repeat"
        self.repeat_btn.clicked.connect(self.choose_repeat)
        dt_vbox.addWidget(self.repeat_btn)
        
        self.time_sec.add_layout(dt_vbox)
        self.body.add_section(self.time_sec)
        
        # If it's a pure AI task (duration-based), configure duration picker
        if self.is_ai:
            self.to_lbl.setVisible(False)
            self.end_p_btn.setVisible(False)
            self.start_p_btn.setText(Translator.translate("ui.60_mins")); self.start_p_btn.translation_key = "ui.60_mins"
            self.start_p_btn.clicked.disconnect()
            self.start_p_btn.clicked.connect(self.choose_duration)
            self.selected_duration = 60
            
        # 4. Deadline Selector (🎯)
        deadline_sec = DialogSection("🎯")
        self.deadline_btn = make_translatable(QPushButton(), "dialog.add_deadline")
        self.deadline_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.deadline_btn.setStyleSheet(self.repeat_btn.styleSheet())
        self.selected_deadline = None
        self.deadline_btn.clicked.connect(self.choose_deadline)
        deadline_sec.add_field(self.deadline_btn)
        self.body.add_section(deadline_sec)
        
        # 5. Description / Attachment Row (📝)
        desc_sec = DialogSection("📝")
        self.desc_le = QLineEdit()
        self.desc_le.setPlaceholderText(Translator.translate("placeholder.add_description_or")); self.desc_le.placeholder_translation_key = "placeholder.add_description_or"
        self.desc_field = DialogField(self.desc_le)
        self.desc_le.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 13px;
                color: #475569;
                padding: 4px 0px;
            }
        """)
        desc_sec.add_field(self.desc_field)
        self.body.add_section(desc_sec)
        
        # 6. List Selector (☰)
        list_sec = DialogSection("☰")
        self.list_cb = QComboBox()
        self.list_cb.addItems(["My Tasks", "University Schedule", "AI Recommended Tasks"])
        self.list_cb.setStyleSheet("""
            QComboBox {
                background-color: #F1F5F9;
                color: #0F172A;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #64748B;
                width: 0; height: 0;
            }
        """)
        list_sec.add_field(self.list_cb)
        self.body.add_section(list_sec)
        
        # 7. Owner / Visibility Settings (👤)
        owner_sec = DialogSection("👤")
        owner_vbox = QVBoxLayout()
        owner_vbox.setSpacing(2)
        
        owner_name = make_translatable(QLabel(), "dialog.kc_henry")
        owner_name.setStyleSheet("font-size: 13px; font-weight: 700; color: #0F172A; border: none;")
        owner_vbox.addWidget(owner_name)
        
        owner_settings = make_translatable(QLabel(), "dialog.free_private")
        owner_settings.setStyleSheet("font-size: 11px; color: #64748B; border: none;")
        owner_vbox.addWidget(owner_settings)
        
        owner_sec.add_layout(owner_vbox)
        self.body.add_section(owner_sec)
        
        self.body.add_stretch()
        self.card_layout.addWidget(self.body, 1)
        
        # Footer
        self.footer = DialogFooter(self)
        
        if self.is_ai and data:
            self.assign_btn = make_translatable(QPushButton(), "ui.assign_to_schedule")
            self.assign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.assign_btn.setStyleSheet("background: #10B981; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
            self.assign_btn.clicked.connect(self.accept_assign)
            self.footer.add_widget_left(self.assign_btn)
            
        self.footer.add_stretch()
        
        if self.is_edit:
            self.del_btn = make_translatable(QPushButton(), "button.delete")
            self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.del_btn.setStyleSheet("background-color: #EF4444; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
            self.del_btn.clicked.connect(self.reject_delete)
            self.footer.add_button(self.del_btn)
            
        self.save_btn = make_translatable(QPushButton(), "button.save")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Google Calendar signature blue pill save button
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A52D6;
                color: white;
                border-radius: 14px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1A73E8;
            }
        """)
        self.save_btn.clicked.connect(self.accept_save)
        self.footer.add_button(self.save_btn)
        
        self.card_layout.addWidget(self.footer)
        
        # Load initial values
        self.selected_day = "Monday"
        self.selected_start_period = 1
        self.selected_end_period = 1
        self.selected_duration = 60
        
        if data:
            self.title_le.setText(str(data.get("title", "")))
            self.selected_day = data.get("day", "Monday")
            self.selected_type = data.get("type", "class")
            self.select_tab(self.selected_type)
            
            if self.is_ai:
                self.selected_duration = int(data.get("duration_min", 60))
                self.start_p_btn.setText(f"{self.selected_duration} mins")
            else:
                self.selected_start_period = int(data.get("period_start", 1))
                self.selected_end_period = int(data.get("period_end", 1))
                self.start_p_btn.setText(f"{self.selected_start_period:02d}:00")
                self.end_p_btn.setText(f"{self.selected_end_period:02d}:00")
                
            self.desc_le.setText(data.get("description", ""))
            if data.get("repeat"):
                self.selected_repeat = data.get("repeat")
                self.repeat_btn.setText(self.selected_repeat)
            if data.get("deadline"):
                self.selected_deadline = data.get("deadline")
                self.deadline_btn.setText(f"Deadline: {self.selected_deadline}")
            if data.get("list_name"):
                self.list_cb.setCurrentText(data.get("list_name"))
                
        self.update_date_display()
        self.title_le.setFocus()
        
    def get_date_for_weekday(self, weekday_str):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if weekday_str not in days:
            return datetime.date.today()
        target_idx = days.index(weekday_str)
        today = datetime.date.today()
        today_idx = today.weekday()
        offset = target_idx - today_idx
        return today + datetime.timedelta(days=offset)
        
    def update_date_display(self):
        dt = self.get_date_for_weekday(self.selected_day)
        self.date_btn.setText(dt.strftime("%A, %B %d"))
        
    def select_tab(self, category_type):
        self.selected_type = category_type
        
        active_style = """
            QPushButton {
                background-color: #E0F2FE;
                color: #0284C7;
                border-radius: 14px;
                padding: 0px 12px;
                font-weight: bold;
                font-size: 11px;
                border: none;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border-radius: 14px;
                padding: 0px 12px;
                font-weight: 600;
                font-size: 11px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """
        self.event_tab.setStyleSheet(active_style if category_type == "class" else inactive_style)
        self.task_tab.setStyleSheet(active_style if category_type == "study_task" else inactive_style)
        self.appt_tab.setStyleSheet(active_style if category_type == "other" else inactive_style)
        
    def choose_date(self):
        initial = self.get_date_for_weekday(self.selected_day)
        popup = DatePickerDialog(initial_date=initial, parent=self)
        popup.date_selected.connect(self._on_date_selected)
        show_popup_below(self.date_btn, popup)
        
    def _on_date_selected(self, dt):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.selected_day = days[dt.weekday()]
        self.update_date_display()
        
    def choose_start_period(self):
        popup = TimePickerDialog(initial_period=self.selected_start_period, parent=self)
        popup.period_selected.connect(self._on_start_period_selected)
        show_popup_below(self.start_p_btn, popup)
        
    def _on_start_period_selected(self, p):
        self.selected_start_period = p
        self.start_p_btn.setText(f"{p:02d}:00")
        if self.selected_end_period < p:
            self.selected_end_period = p
            self.end_p_btn.setText(f"{p:02d}:00")
            
    def choose_end_period(self):
        popup = TimePickerDialog(initial_period=self.selected_end_period, parent=self)
        popup.period_selected.connect(self._on_end_period_selected)
        show_popup_below(self.end_p_btn, popup)
        
    def _on_end_period_selected(self, p):
        if p >= self.selected_start_period:
            self.selected_end_period = p
            self.end_p_btn.setText(f"{p:02d}:00")
        else:
            self.selected_end_period = self.selected_start_period
            self.end_p_btn.setText(f"{self.selected_start_period:02d}:00")
            
    def choose_duration(self):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; } QMenu::item { padding: 8px 16px; color: #0F172A; } QMenu::item:selected { background-color: #F1F5F9; }")
        durations = [30, 45, 60, 90, 120, 180]
        for d in durations:
            act = menu.addAction(f"{d} mins")
            act.triggered.connect(lambda checked, val=d: self._set_duration(val))
        menu.exec(self.start_p_btn.mapToGlobal(QPoint(0, self.start_p_btn.height())))
        
    def _set_duration(self, d):
        self.selected_duration = d
        self.start_p_btn.setText(f"{d} mins")
        
    def choose_repeat(self):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; } QMenu::item { padding: 8px 16px; color: #0F172A; } QMenu::item:selected { background-color: #F1F5F9; }")
        options = ["Does not repeat", "Daily", "Weekly", "Monthly", "Yearly"]
        for opt in options:
            act = menu.addAction(opt)
            act.triggered.connect(lambda checked, val=opt: self._set_repeat(val))
        menu.exec(self.repeat_btn.mapToGlobal(QPoint(0, self.repeat_btn.height())))
        
    def _set_repeat(self, opt):
        self.selected_repeat = opt
        self.repeat_btn.setText(opt)
        
    def choose_deadline(self):
        popup = DatePickerDialog(parent=self)
        popup.date_selected.connect(self._on_deadline_selected)
        show_popup_below(self.deadline_btn, popup)
        
    def _on_deadline_selected(self, dt):
        self.selected_deadline = dt.strftime("%Y-%m-%d")
        self.deadline_btn.setText(f"Deadline: {self.selected_deadline}")
        
    def on_more_options(self):
        self.action = "more_options"
        self.done(10)
        
    def reject_delete(self):
        conf = ConfirmationDialog("Delete Event", "Are you sure you want to delete this event/class?", parent=self)
        if conf.exec():
            self.action = "delete"
            self.done(QDialog.DialogCode.Accepted)
            
    def accept_assign(self):
        self.action = "assign"
        self.done(QDialog.DialogCode.Accepted)
        
    def accept_save(self):
        title = self.title_le.text().strip()
        if not title:
            self.title_field.set_error("Title is required")
            self.title_le.setFocus()
            return
            
        self.title_field.clear_error()
        self.action = "save"
        self.done(QDialog.DialogCode.Accepted)
        
    def get_data(self):
        room_val = self.data.get("room", "") if self.data else ""
        group_val = self.data.get("group", "") if self.data else ""
        res = {
            "title": self.title_le.text().strip(),
            "day": self.selected_day,
            "period_start": self.selected_start_period,
            "period_end": self.selected_end_period,
            "type": self.selected_type,
            "room": room_val,
            "group": group_val,
            "description": self.desc_le.text().strip(),
            "repeat": self.selected_repeat,
            "deadline": self.selected_deadline,
            "list_name": self.list_cb.currentText(),
            "completed": self.data.get("completed", False) if self.data else False
        }
        if self.is_ai:
            res["duration_min"] = self.selected_duration
        if self.data:
            for k, v in self.data.items():
                if k not in res:
                    res[k] = v
        return res
        
    def update_color_button_style(self):
        colors = {
            "class": ("#0284C7", "Class (Blue)"),
            "makeup": ("#A16207", "Makeup (Yellow)"),
            "self_study": ("#7E22CE", "Self Study (Purple)"),
            "exam": ("#B91C1C", "Exam (Red)"),
            "study_task": ("#15803D", "Study Task (Green)"),
            "other": ("#475569", "Other (Gray)")
        }
        hex_val, name = colors.get(self.selected_type, colors["other"])
        self.color_btn.setText(name)
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_val};
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
        """)
        
    def choose_date(self):
        popup = DatePickerDialog(parent=self)
        popup.date_selected.connect(self._on_date_selected)
        show_popup_below(self.date_btn, popup)
        
    def _on_date_selected(self, dt):
        # Map to weekday string
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.selected_day = days[dt.weekday()]
        self.date_btn.setText(f"{self.selected_day} ({dt.strftime('%b %d')})")
        
    def choose_start_period(self):
        popup = TimePickerDialog(initial_period=self.selected_start_period, parent=self)
        popup.period_selected.connect(self._on_start_period_selected)
        show_popup_below(self.start_p_btn, popup)
        
    def _on_start_period_selected(self, p):
        self.selected_start_period = p
        self.start_p_btn.setText(f"Period {p}")
        if self.selected_end_period < p:
            self.selected_end_period = p
            self.end_p_btn.setText(f"Period {p}")
            
    def choose_end_period(self):
        popup = TimePickerDialog(initial_period=self.selected_end_period, parent=self)
        popup.period_selected.connect(self._on_end_period_selected)
        show_popup_below(self.end_p_btn, popup)
        
    def _on_end_period_selected(self, p):
        if p >= self.selected_start_period:
            self.selected_end_period = p
            self.end_p_btn.setText(f"Period {p}")
        else:
            # End must be >= start
            self.selected_end_period = self.selected_start_period
            self.end_p_btn.setText(f"Period {self.selected_start_period}")
            
    def choose_duration(self):
        # Show a simple dialog list of duration options
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; } QMenu::item { padding: 8px 16px; color: #0F172A; } QMenu::item:selected { background-color: #F1F5F9; }")
        
        durations = [30, 45, 60, 90, 120, 180]
        for d in durations:
            act = menu.addAction(f"{d} mins")
            act.triggered.connect(lambda checked, val=d: self._set_duration(val))
        menu.exec(self.start_p_btn.mapToGlobal(QPoint(0, self.start_p_btn.height())))
        
    def _set_duration(self, d):
        self.selected_duration = d
        self.start_p_btn.setText(f"{d} mins")
        
    def choose_color(self):
        popup = ColorPickerDialog(initial_color_type=self.selected_type, parent=self)
        popup.color_selected.connect(self._on_color_selected)
        show_popup_below(self.color_btn, popup)
        
    def _on_color_selected(self, name):
        self.selected_type = name
        self.update_color_button_style()
        
    def on_more_options(self):
        self.action = "more_options"
        # Return 10 to signify switching to Full Event Dialog
        self.done(10)
        
    def reject_delete(self):
        # Open Confirmation Dialog
        conf = ConfirmationDialog("Delete Event", "Are you sure you want to delete this event/class?", parent=self)
        if conf.exec():
            self.action = "delete"
            self.done(QDialog.DialogCode.Accepted)
            
    def accept_assign(self):
        self.action = "assign"
        self.done(QDialog.DialogCode.Accepted)
        
    def accept_save(self):
        # Real-time validation
        title = self.title_le.text().strip()
        if not title:
            self.title_field.set_error("Title is required")
            self.title_le.setFocus()
            return
            
        self.title_field.clear_error()
        self.action = "save"
        self.done(QDialog.DialogCode.Accepted)
        
    def get_data(self):
        room_val = self.data.get("room", "") if self.data else ""
        group_val = self.data.get("group", "") if self.data else ""
        
        # Return a merged dictionary
        res = {
            "title": self.title_le.text().strip(),
            "day": self.selected_day,
            "period_start": self.selected_start_period,
            "period_end": self.selected_end_period,
            "type": self.selected_type,
            "room": room_val,
            "group": group_val,
            "completed": self.data.get("completed", False) if self.data else False
        }
        
        if self.is_ai:
            res["duration_min"] = self.selected_duration
            
        # Copy other fields if they exist in self.data
        if self.data:
            for k, v in self.data.items():
                if k not in res:
                    res[k] = v
                    
        return res

class FullEventDialog(BaseDialog):
    def __init__(self, data=None, is_ai=False, click_position=None, parent=None):
        super().__init__(parent, size_class="medium", click_position=click_position)
        self.data = data
        self.is_ai = is_ai
        self.action = "cancel"
        
        title = "Edit Event Details" if data else "Create Detailed Event"
        
        # Header
        self.header = DialogHeader(title, icon_char="🗓️", has_more=False, parent=self)
        self.header.close_clicked.connect(self.reject)
        self.card_layout.addWidget(self.header)
        
        # Body
        self.body = DialogBody(self)
        
        # 1. Title Field
        self.title_le = QLineEdit()
        self.title_le.setPlaceholderText(Translator.translate("placeholder.add_title")); self.title_le.placeholder_translation_key = "placeholder.add_title"
        self.title_le.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                padding: 4px 0px;
                background: transparent;
                color: #0F172A;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2563EB;
            }
        """)
        self.title_field = DialogField(self.title_le)
        title_sec = DialogSection(" ")
        title_sec.add_field(self.title_field)
        self.body.add_section(title_sec)
        
        # 2. Date & Time Row
        time_sec = DialogSection("🕒")
        time_h = QHBoxLayout()
        time_h.setSpacing(8)
        
        self.date_btn = make_translatable(QPushButton(), "dialog.select_day")
        self.date_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.date_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.selected_day = "Monday"
        self.date_btn.clicked.connect(self.choose_date)
        time_h.addWidget(self.date_btn)
        
        self.start_p_btn = make_translatable(QPushButton(), "ui.period_1")
        self.start_p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_p_btn.setStyleSheet(self.date_btn.styleSheet())
        self.selected_start_period = 1
        self.start_p_btn.clicked.connect(self.choose_start_period)
        time_h.addWidget(self.start_p_btn)
        
        to_lbl = make_translatable(QLabel(), "dialog.to")
        to_lbl.setStyleSheet("color: #64748B; font-weight: 500; font-size: 13px;")
        time_h.addWidget(to_lbl)
        
        self.end_p_btn = make_translatable(QPushButton(), "ui.period_1")
        self.end_p_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_p_btn.setStyleSheet(self.date_btn.styleSheet())
        self.selected_end_period = 1
        self.end_p_btn.clicked.connect(self.choose_end_period)
        time_h.addWidget(self.end_p_btn)
        
        time_sec.add_layout(time_h)
        
        # All Day / Repeat options
        options_h = QHBoxLayout()
        options_h.setSpacing(16)
        
        self.all_day_chk = make_translatable(QCheckBox(), "dialog.all_day")
        self.all_day_chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.all_day_chk.setStyleSheet("QCheckBox { color: #475569; font-size: 12px; font-weight: 500; }")
        self.all_day_chk.stateChanged.connect(self.on_all_day_toggled)
        options_h.addWidget(self.all_day_chk)
        
        self.repeat_cb = QComboBox()
        self.repeat_cb.addItems(["Does not repeat", "Daily", "Weekly", "Every weekday (Monday to Friday)", "Custom..."])
        self.repeat_cb.setStyleSheet("""
            QComboBox {
                background: transparent; border: none; color: #475569; font-size: 12px; font-weight: 600; padding: 4px;
            }
            QComboBox:hover {
                background-color: #F1F5F9; border-radius: 4px;
            }
        """)
        options_h.addWidget(self.repeat_cb)
        options_h.addStretch()
        
        time_sec.add_layout(options_h)
        self.body.add_section(time_sec)
        
        if self.is_ai:
            to_lbl.setVisible(False)
            self.end_p_btn.setVisible(False)
            self.start_p_btn.setText(Translator.translate("ui.60_mins")); self.start_p_btn.translation_key = "ui.60_mins"
            self.start_p_btn.clicked.disconnect()
            self.start_p_btn.clicked.connect(self.choose_duration)
            self.selected_duration = 60
            self.all_day_chk.setVisible(False)
            
        # 3. Location / Room
        loc_sec = DialogSection("📍")
        self.room_le = QLineEdit()
        self.room_le.setPlaceholderText(Translator.translate("placeholder.add_location_room")); self.room_le.placeholder_translation_key = "placeholder.add_location_room"
        self.room_field = DialogField(self.room_le)
        loc_sec.add_field(self.room_field)
        self.body.add_section(loc_sec)
        
        # 4. Guests
        guests_sec = DialogSection("👥")
        self.guests_le = QLineEdit()
        self.guests_le.setPlaceholderText(Translator.translate("placeholder.add_guests_email")); self.guests_le.placeholder_translation_key = "placeholder.add_guests_email"
        self.guests_field = DialogField(self.guests_le)
        guests_sec.add_field(self.guests_field)
        self.body.add_section(guests_sec)
        
        # 5. Video Meeting button
        video_sec = DialogSection("📹")
        self.video_btn = make_translatable(QPushButton(), "button.add_google_meet")
        self.video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.has_video_meeting = False
        self.video_btn.clicked.connect(self.toggle_video_meeting)
        video_sec.add_field(self.video_btn)
        self.body.add_section(video_sec)
        
        # 6. Notification setting
        notify_sec = DialogSection("🔔")
        notify_h = QHBoxLayout()
        notify_h.setSpacing(12)
        
        self.notify_cb = QComboBox()
        self.notify_cb.addItems(["10 minutes before", "30 minutes before", "1 hour before", "1 day before", "Custom..."])
        self.notify_field = DialogField(self.notify_cb)
        notify_h.addWidget(self.notify_field)
        
        self.notify_type_cb = QComboBox()
        self.notify_type_cb.addItems(["Notification", "Email"])
        self.notify_type_field = DialogField(self.notify_type_cb)
        notify_h.addWidget(self.notify_type_field)
        
        notify_sec.add_layout(notify_h)
        self.body.add_section(notify_sec)
        
        # 7. Category Color
        color_sec = DialogSection("🎨")
        self.color_btn = make_translatable(QPushButton(), "dialog.class_blue")
        self.color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.selected_type = "class"
        if self.is_ai:
            self.selected_type = "study_task"
            
        self.update_color_button_style()
        self.color_btn.clicked.connect(self.choose_color)
        color_sec.add_field(self.color_btn)
        self.body.add_section(color_sec)
        
        # 8. Description & Attachments
        desc_sec = DialogSection("📝")
        self.desc_te = QTextEdit()
        self.desc_te.setPlaceholderText(Translator.translate("placeholder.add_description_or_1")); self.desc_te.placeholder_translation_key = "placeholder.add_description_or_1"
        self.desc_te.setFixedHeight(80)
        self.desc_field = DialogField(self.desc_te)
        desc_sec.add_field(self.desc_field)
        
        # Attachment Button
        self.attach_btn = make_translatable(QPushButton(), "dialog.add_attachment")
        self.attach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        self.attachments = []
        self.attach_btn.clicked.connect(self.add_attachment)
        desc_sec.add_field(self.attach_btn)
        self.body.add_section(desc_sec)
        
        # 9. Free/Busy & Visibility
        options_sec = DialogSection("⚙️")
        opt_h = QHBoxLayout()
        opt_h.setSpacing(12)
        
        self.busy_cb = QComboBox()
        self.busy_cb.addItems(["Busy", "Free"])
        self.busy_field = DialogField(self.busy_cb, "Availability")
        opt_h.addWidget(self.busy_field)
        
        self.visibility_cb = QComboBox()
        self.visibility_cb.addItems(["Default visibility", "Public", "Private"])
        self.visibility_field = DialogField(self.visibility_cb, "Visibility")
        opt_h.addWidget(self.visibility_field)
        
        options_sec.add_layout(opt_h)
        self.body.add_section(options_sec)
        
        self.body.add_stretch()
        self.card_layout.addWidget(self.body, 1)
        
        # Footer
        self.footer = DialogFooter(self)
        
        if is_ai and data:
            self.assign_btn = make_translatable(QPushButton(), "ui.assign_to_schedule")
            self.assign_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.assign_btn.setStyleSheet("background: #10B981; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
            self.assign_btn.clicked.connect(self.accept_assign)
            self.footer.add_widget_left(self.assign_btn)
            
        self.footer.add_stretch()
        
        # Action Buttons
        btn_sub_style = """
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #E2E8F0;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """
        
        if data:
            self.del_btn = make_translatable(QPushButton(), "button.delete")
            self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.del_btn.setStyleSheet("background-color: #EF4444; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
            self.del_btn.clicked.connect(self.reject_delete)
            self.footer.add_button(self.del_btn)
            
        self.cancel_btn = make_translatable(QPushButton(), "button.cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet(btn_sub_style)
        self.cancel_btn.clicked.connect(self.reject)
        self.footer.add_button(self.cancel_btn)
        
        self.save_btn = make_translatable(QPushButton(), "button.save")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("background-color: #2563EB; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
        self.save_btn.clicked.connect(self.accept_save)
        self.footer.add_button(self.save_btn)
        
        self.card_layout.addWidget(self.footer)
        
        # Load initial values
        if data:
            self.title_le.setText(str(data.get("title", "")))
            self.selected_day = data.get("day", "Monday")
            self.date_btn.setText(self.selected_day)
            
            if self.is_ai:
                self.selected_duration = int(data.get("duration_min", 60))
                self.start_p_btn.setText(f"{self.selected_duration} mins")
            else:
                self.selected_start_period = int(data.get("period_start", 1))
                self.selected_end_period = int(data.get("period_end", 1))
                self.start_p_btn.setText(f"{self.selected_start_period:02d}:00")
                self.end_p_btn.setText(f"{self.selected_end_period:02d}:00")
                
            self.selected_type = data.get("type", "study_task" if is_ai else "class")
            self.update_color_button_style()
            
            # Load room/group
            room = data.get("room", "") or data.get("group", "")
            self.room_le.setText(str(room))
            
            # Load other optional details
            self.guests_le.setText(str(data.get("guests", "")))
            self.desc_te.setText(str(data.get("description", "")))
            
            self.all_day_chk.setChecked(bool(data.get("all_day", False)))
            self.repeat_cb.setCurrentText(data.get("repeat", "Does not repeat"))
            self.notify_cb.setCurrentText(data.get("notification", "30 minutes before"))
            self.notify_type_cb.setCurrentText(data.get("notification_type", "Notification"))
            self.busy_cb.setCurrentText(data.get("availability", "Busy"))
            self.visibility_cb.setCurrentText(data.get("visibility", "Default visibility"))
            
            self.has_video_meeting = bool(data.get("video_meeting", False))
            self.update_video_button_style()
            
        self.title_le.setFocus()
        
    def update_color_button_style(self):
        colors = {
            "class": ("#0284C7", "Class (Blue)"),
            "makeup": ("#A16207", "Makeup (Yellow)"),
            "self_study": ("#7E22CE", "Self Study (Purple)"),
            "exam": ("#B91C1C", "Exam (Red)"),
            "study_task": ("#15803D", "Study Task (Green)"),
            "other": ("#475569", "Other (Gray)")
        }
        hex_val, name = colors.get(self.selected_type, colors["other"])
        self.color_btn.setText(name)
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_val};
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
        """)
        
    def choose_date(self):
        popup = DatePickerDialog(parent=self)
        popup.date_selected.connect(self._on_date_selected)
        show_popup_below(self.date_btn, popup)
        
    def _on_date_selected(self, dt):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.selected_day = days[dt.weekday()]
        self.date_btn.setText(f"{self.selected_day} ({dt.strftime('%b %d')})")
        
    def choose_start_period(self):
        popup = TimePickerDialog(initial_period=self.selected_start_period, parent=self)
        popup.period_selected.connect(self._on_start_period_selected)
        show_popup_below(self.start_p_btn, popup)
        
    def _on_start_period_selected(self, p):
        self.selected_start_period = p
        self.start_p_btn.setText(f"{p:02d}:00")
        if self.selected_end_period < p:
            self.selected_end_period = p
            self.end_p_btn.setText(f"{p:02d}:00")
            
    def choose_end_period(self):
        popup = TimePickerDialog(initial_period=self.selected_end_period, parent=self)
        popup.period_selected.connect(self._on_end_period_selected)
        show_popup_below(self.end_p_btn, popup)
        
    def _on_end_period_selected(self, p):
        if p >= self.selected_start_period:
            self.selected_end_period = p
            self.end_p_btn.setText(f"{p:02d}:00")
        else:
            self.selected_end_period = self.selected_start_period
            self.end_p_btn.setText(f"{self.selected_start_period:02d}:00")
            
    def choose_duration(self):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 8px; } QMenu::item { padding: 8px 16px; color: #0F172A; } QMenu::item:selected { background-color: #F1F5F9; }")
        
        durations = [30, 45, 60, 90, 120, 180]
        for d in durations:
            act = menu.addAction(f"{d} mins")
            act.triggered.connect(lambda checked, val=d: self._set_duration(val))
        menu.exec(self.start_p_btn.mapToGlobal(QPoint(0, self.start_p_btn.height())))
        
    def _set_duration(self, d):
        self.selected_duration = d
        self.start_p_btn.setText(f"{d} mins")
        
    def on_all_day_toggled(self, state):
        is_checked = state == Qt.CheckState.Checked.value or state == True
        self.start_p_btn.setEnabled(not is_checked)
        self.end_p_btn.setEnabled(not is_checked)
        if is_checked:
            self.selected_start_period = 1
            self.selected_end_period = 10
            self.start_p_btn.setText(Translator.translate("ui.period_1")); self.start_p_btn.translation_key = "ui.period_1"
            self.end_p_btn.setText(Translator.translate("ui.period_10")); self.end_p_btn.translation_key = "ui.period_10"
            
    def choose_color(self):
        popup = ColorPickerDialog(initial_color_type=self.selected_type, parent=self)
        popup.color_selected.connect(self._on_color_selected)
        show_popup_below(self.color_btn, popup)
        
    def _on_color_selected(self, name):
        self.selected_type = name
        self.update_color_button_style()
        
    def toggle_video_meeting(self):
        self.has_video_meeting = not self.has_video_meeting
        self.update_video_button_style()
        
    def update_video_button_style(self):
        if self.has_video_meeting:
            self.video_btn.setText(Translator.translate("ui.google_meet_link")); self.video_btn.translation_key = "ui.google_meet_link"
            self.video_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E0F2FE;
                    color: #0369A1;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: bold;
                    font-size: 13px;
                    border: 1px solid #BAE6FD;
                }
                QPushButton:hover {
                    background-color: #F0F9FF;
                }
            """)
        else:
            self.video_btn.setText(Translator.translate("button.add_google_meet")); self.video_btn.translation_key = "button.add_google_meet"
            self.video_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
            """)
            
    def add_attachment(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if filename:
            import os
            basename = os.path.basename(filename)
            self.attachments.append(filename)
            self.attach_btn.setText(f"📎 Added: {basename}")
            
    def reject_delete(self):
        conf = ConfirmationDialog("Delete Event", "Are you sure you want to delete this event/class?", parent=self)
        if conf.exec():
            self.action = "delete"
            self.done(QDialog.DialogCode.Accepted)
            
    def accept_assign(self):
        self.action = "assign"
        self.done(QDialog.DialogCode.Accepted)
        
    def accept_save(self):
        title = self.title_le.text().strip()
        if not title:
            self.title_field.set_error("Title is required")
            self.title_le.setFocus()
            return
            
        self.title_field.clear_error()
        self.action = "save"
        self.done(QDialog.DialogCode.Accepted)
        
    def get_data(self):
        # Merge all fields into result dict
        res = {
            "title": self.title_le.text().strip(),
            "day": self.selected_day,
            "period_start": self.selected_start_period,
            "period_end": self.selected_end_period,
            "type": self.selected_type,
            "room": self.room_le.text().strip(),
            "guests": self.guests_le.text().strip(),
            "description": self.desc_te.toPlainText().strip(),
            "all_day": self.all_day_chk.isChecked(),
            "repeat": self.repeat_cb.currentText(),
            "notification": self.notify_cb.currentText(),
            "notification_type": self.notify_type_cb.currentText(),
            "availability": self.busy_cb.currentText(),
            "visibility": self.visibility_cb.currentText(),
            "video_meeting": self.has_video_meeting,
            "completed": self.data.get("completed", False) if self.data else False
        }
        
        if self.is_ai:
            res["duration_min"] = self.selected_duration
            
        # Copy other fields from self.data
        if self.data:
            for k, v in self.data.items():
                if k not in res:
                    res[k] = v
                    
        return res

class ConfirmationDialog(BaseDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent, size_class="small")
        self.dialog_height = 200
        
        # Header
        self.header = DialogHeader(title, icon_char="⚠️", has_more=False, parent=self)
        self.header.close_clicked.connect(self.reject)
        self.card_layout.addWidget(self.header)
        
        # Body
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(24, 16, 24, 16)
        
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #475569; font-size: 14px; font-weight: 500; font-family: 'Inter', sans-serif; background: transparent; border: none;")
        body_layout.addWidget(msg_lbl)
        
        self.card_layout.addWidget(body_widget, 1)
        
        # Footer
        self.footer = DialogFooter(self)
        self.footer.add_stretch()
        
        self.cancel_btn = make_translatable(QPushButton(), "button.cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #E2E8F0;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        self.footer.add_button(self.cancel_btn)
        
        self.action_btn = make_translatable(QPushButton(), "dialog.confirm")
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.action_btn.clicked.connect(self.accept)
        self.footer.add_button(self.action_btn)
        
        self.card_layout.addWidget(self.footer)

class SettingsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent, size_class="large")
        
        # Header
        self.header = DialogHeader("Settings", icon_char="⚙️", has_more=False, parent=self)
        self.header.close_clicked.connect(self.reject)
        self.card_layout.addWidget(self.header)
        
        # Content layout split: Left sidebar, Right Stacked content
        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)
        
        # Left Sidebar
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFixedWidth(200)
        self.sidebar_list.setStyleSheet("""
            QListWidget {
                background-color: #F8FAFC;
                border: none;
                border-right: 1px solid #E2E8F0;
                padding: 12px 0px;
            }
            QListWidget::item {
                height: 40px;
                padding-left: 20px;
                color: #475569;
                font-weight: 500;
                font-size: 13px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
            QListWidget::item:selected {
                background-color: #E2E8F0;
                color: #2563EB;
                font-weight: bold;
            }
        """)
        split_layout.addWidget(self.sidebar_list)
        
        # Right Stacked Widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #FFFFFF;")
        split_layout.addWidget(self.stacked_widget, 1)
        
        # 1. Page General
        gen_page = QScrollArea()
        gen_page.setWidgetResizable(True)
        gen_page.setFrameShape(QScrollArea.Shape.NoFrame)
        gen_content = QWidget()
        gen_content.setStyleSheet("background: transparent;")
        gen_lay = QVBoxLayout(gen_content)
        gen_lay.setContentsMargins(24, 24, 24, 24)
        gen_lay.setSpacing(20)
        
        title_gen = make_translatable(QLabel(), "settings.section.general")
        title_gen.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        gen_lay.addWidget(title_gen)
        
        # Settings field 1
        dur_cb = QComboBox()
        dur_cb.addItems(["30 minutes", "45 minutes (Default)", "60 minutes", "90 minutes"])
        dur_field = DialogField(dur_cb, "Default Event Duration")
        gen_lay.addWidget(dur_field)
        
        # Settings field 2
        day_cb = QComboBox()
        day_cb.addItems(["Sunday", "Monday (Default)", "Saturday"])
        day_field = DialogField(day_cb, "Start Week On")
        gen_lay.addWidget(day_field)
        
        gen_lay.addStretch()
        gen_page.setWidget(gen_content)
        self.stacked_widget.addWidget(gen_page)
        
        # 2. Page Notifications
        notif_page = QScrollArea()
        notif_page.setWidgetResizable(True)
        notif_page.setFrameShape(QScrollArea.Shape.NoFrame)
        notif_content = QWidget()
        notif_content.setStyleSheet("background: transparent;")
        notif_lay = QVBoxLayout(notif_content)
        notif_lay.setContentsMargins(24, 24, 24, 24)
        notif_lay.setSpacing(20)
        
        title_notif = make_translatable(QLabel(), "dialog.notifications_settings")
        title_notif.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        notif_lay.addWidget(title_notif)
        
        # Notifications checkbox 1
        notif1_chk = make_translatable(QCheckBox(), "dialog.enable_desktop_notifications")
        notif1_chk.setChecked(True)
        notif1_chk.setStyleSheet("color: #475569; font-size: 13px; font-weight: 500;")
        notif_lay.addWidget(notif1_chk)
        
        # Notifications checkbox 2
        notif2_chk = make_translatable(QCheckBox(), "dialog.receive_email_reminders")
        notif2_chk.setChecked(False)
        notif2_chk.setStyleSheet("color: #475569; font-size: 13px; font-weight: 500;")
        notif_lay.addWidget(notif2_chk)
        
        notif_lay.addStretch()
        notif_page.setWidget(notif_content)
        self.stacked_widget.addWidget(notif_page)
        
        # Add sidebar items
        self.sidebar_list.addItem(QListWidgetItem("General"))
        self.sidebar_list.addItem(QListWidgetItem("Notifications"))
        self.sidebar_list.setCurrentRow(0)
        self.sidebar_list.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)
        
        self.card_layout.addWidget(split_widget, 1)
        
        # Footer
        self.footer = DialogFooter(self)
        self.footer.add_stretch()
        
        self.save_btn = make_translatable(QPushButton(), "dialog.done")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet("background-color: #2563EB; color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; border: none;")
        self.save_btn.clicked.connect(self.accept)
        self.footer.add_button(self.save_btn)
        
        self.card_layout.addWidget(self.footer)
