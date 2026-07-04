from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout, 
                             QSizePolicy, QComboBox, QDialog, QLineEdit, QFormLayout, 
                             QMessageBox, QCheckBox, QGraphicsDropShadowEffect, QSlider, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QSize
from PyQt6.QtGui import QColor, QFont, QCursor, QPainter, QPen, QBrush
import datetime
import calendar

from core.translation.base_translatable_widget import BaseTranslatableWidget, BaseTranslatableFrame, make_translatable
from core.translation.translator import Translator
from database import crud
from ui_core.google_calendar_dialogs import QuickCreateDialog, FullEventDialog, ConfirmationDialog, SettingsDialog

class ClickableCell(QFrame):
    clicked = pyqtSignal(str, int, QPoint) # day, period, click_pos

    def __init__(self, day, period, parent=None):
        super().__init__(parent)
        self.day = day
        self.period = period
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day, self.period, QCursor.pos())

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Dynamic red current-time line indicator
        now = datetime.datetime.now()
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today_wday = days_of_week[now.weekday()]
        
        if self.day == today_wday:
            # Map periods to minutes since 00:00
            periods_times = {
                h: (h*60, (h+1)*60) for h in range(0, 24)
            }
            
            if self.period in periods_times:
                start_m, end_m = periods_times[self.period]
                curr_m = now.hour * 60 + now.minute
                if start_m <= curr_m < end_m:
                    ratio = (curr_m - start_m) / (end_m - start_m)
                    y = int(ratio * self.height())
                    
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    
                    # Draw red line
                    pen = QPen(QColor(239, 68, 68), 2)
                    painter.setPen(pen)
                    painter.drawLine(0, y, self.width(), y)
                    
                    # Draw small circle on the left edge
                    brush = QBrush(QColor(239, 68, 68))
                    painter.setBrush(brush)
                    painter.drawEllipse(0, y - 4, 8, 8)


class DayHeaderWidget(QWidget):
    def __init__(self, day_name, date_val, is_today=False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Day name label (e.g. SAT)
        self.day_label = QLabel(day_name[:3].upper())
        self.day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_today:
            self.day_label.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 800; border: none; background: transparent; font-family: 'Inter', sans-serif;")
        else:
            self.day_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; border: none; background: transparent; font-family: 'Inter', sans-serif;")
            
        # Day number label (e.g. 4)
        self.num_label = QLabel(str(date_val.day))
        self.num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if is_today:
            self.num_label.setFixedSize(36, 36)
            self.num_label.setStyleSheet("""
                background-color: #2563EB;
                color: white;
                font-size: 16px;
                font-weight: 800;
                border-radius: 18px;
                border: none;
                font-family: 'Inter', sans-serif;
            """)
        else:
            self.num_label.setStyleSheet("color: #0F172A; font-size: 16px; font-weight: 600; border: none; background: transparent; font-family: 'Inter', sans-serif;")
            
        layout.addWidget(self.day_label)
        layout.addWidget(self.num_label)
        
        self.setStyleSheet("background-color: #FFFFFF; border: none;")

class PendingTasksPill(QFrame):
    def __init__(self, count, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #E0F2FE;
                border-radius: 12px;
                border: none;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_lbl = QLabel("⏱️")
        icon_lbl.setStyleSheet("font-size: 11px; background: transparent; border: none;")
        
        # Text
        txt_lbl = QLabel(f"{count} pending tasks")
        txt_lbl.setStyleSheet("color: #0369A1; font-weight: 700; font-size: 11px; background: transparent; border: none; font-family: 'Inter', sans-serif;")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(txt_lbl)
        self.setFixedHeight(24)

class AllDayCell(QFrame):
    def __init__(self, day_name, parent=None):
        super().__init__(parent)
        self.day_name = day_name
        self.setStyleSheet("background: transparent; border: none;")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

class CalendarGridContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #FFFFFF;")

    def paintEvent(self, event):
        p = QPainter(self)
        try:
            p.fillRect(self.rect(), QColor("#FFFFFF"))
            p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            pen = QPen(QColor("#E2E8F0"), 1)
            p.setPen(pen)
            
            # Collect lines positions
            x_positions = set()
            y_positions = set()
            
            grid_left = 64
            grid_right = self.width()
            grid_top = 0
            grid_bottom = self.height()
            
            for child in self.findChildren(QWidget):
                if not child.isVisible():
                    continue
                geom = child.geometry()
                
                if isinstance(child, (ClickableCell, AllDayCell, DayHeaderWidget)):
                    x_positions.add(geom.right())
                    y_positions.add(geom.bottom())
                    if isinstance(child, DayHeaderWidget):
                        grid_top = max(grid_top, geom.bottom())
                elif hasattr(child, "text") and child.text() == "GMT+07":
                    x_positions.add(geom.right())
                    y_positions.add(geom.bottom())
                    
            # Draw vertical lines (from grid_top to grid_bottom)
            for x in x_positions:
                p.drawLine(x, grid_top, x, grid_bottom)
                
            # Draw horizontal lines (from grid_left to grid_right)
            for y in y_positions:
                p.drawLine(grid_left, y, grid_right, y)
        finally:
            p.end()


class ClickableMonthCell(QFrame):
    clicked = pyqtSignal(datetime.date, QPoint)
    double_clicked = pyqtSignal(datetime.date)

    def __init__(self, date_val, is_current_month, parent=None):
        super().__init__(parent)
        self.date_val = date_val
        self.is_current_month = is_current_month
        self.setObjectName("MonthCell")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            #MonthCell {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
                border-right: 1px solid #E2E8F0;
                min-height: 90px;
            }
            #MonthCell:hover { background-color: #F8FAFC; }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.date_val, QCursor.pos())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.date_val)


class MiniMonthWidget(QWidget):
    month_clicked = pyqtSignal(datetime.date)

    def __init__(self, year, month, parent=None):
        super().__init__(parent)
        self.year = year
        self.month = month
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(6)

        # Month Year Header
        hdr = QHBoxLayout()
        month_name = datetime.date(self.year, self.month, 1).strftime("%B %Y")
        self.hdr_lbl = QLabel(month_name)
        self.hdr_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0F172A; font-family: 'Inter', sans-serif;")
        hdr.addWidget(self.hdr_lbl)
        hdr.addStretch()

        # Navigation arrows
        self.prev_btn = QPushButton("‹")
        self.next_btn = QPushButton("›")
        for btn in (self.prev_btn, self.next_btn):
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #64748B; border: none; font-size: 14px; font-weight: bold;
                    padding: 0px;
                }
                QPushButton:hover { background-color: #F1F5F9; color: #0F172A; border-radius: 4px; }
            """)
        self.prev_btn.clicked.connect(self.navigate_prev)
        self.next_btn.clicked.connect(self.navigate_next)
        hdr.addWidget(self.prev_btn)
        hdr.addWidget(self.next_btn)
        self.layout.addLayout(hdr)

        # Days Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        self.grid.setContentsMargins(0, 0, 0, 0)

        # Weekday headers: M T W T F S S
        wdays = ["M", "T", "W", "T", "F", "S", "S"]
        for col, wd in enumerate(wdays):
            lbl = QLabel(wd)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: 700; font-family: 'Inter', sans-serif;")
            self.grid.addWidget(lbl, 0, col)

        self.populate_days()
        self.layout.addLayout(self.grid)

    def navigate_prev(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        month_name = datetime.date(self.year, self.month, 1).strftime("%B %Y")
        self.hdr_lbl.setText(month_name)
        self.populate_days()

    def navigate_next(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        month_name = datetime.date(self.year, self.month, 1).strftime("%B %Y")
        self.hdr_lbl.setText(month_name)
        self.populate_days()

    def populate_days(self):
        # Clear previous day widgets in grid (row > 0)
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            pos = self.grid.getItemPosition(i)
            if pos[0] > 0:
                w = item.widget()
                if w:
                    w.deleteLater()

        weeks = calendar.monthcalendar(self.year, self.month)
        today = datetime.date.today()

        for row_idx, week in enumerate(weeks):
            for col_idx, day in enumerate(week):
                if day == 0:
                    lbl = QLabel("")
                    self.grid.addWidget(lbl, row_idx + 1, col_idx)
                else:
                    btn = QPushButton(str(day))
                    btn.setFixedSize(24, 24)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)

                    is_today = (self.year == today.year and self.month == today.month and day == today.day)
                    if is_today:
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #2563EB; color: white; border: none; border-radius: 12px;
                                font-size: 10px; font-weight: bold; font-family: 'Inter', sans-serif;
                                padding: 0px;
                            }
                        """)
                    else:
                        btn.setStyleSheet("""
                            QPushButton {
                                background: transparent; color: #334155; border: none; border-radius: 12px;
                                font-size: 10px; font-weight: 500; font-family: 'Inter', sans-serif;
                                padding: 0px;
                            }
                            QPushButton:hover { background-color: #F1F5F9; }
                        """)

                    click_date = datetime.date(self.year, self.month, day)
                    btn.clicked.connect(lambda checked, d=click_date: self.month_clicked.emit(d))
                    self.grid.addWidget(btn, row_idx + 1, col_idx)


class PlannerToolbar(BaseTranslatableFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 1. Left side controls
        # Hamburger Menu
        self.hamburger_btn = QPushButton("☰")
        self.hamburger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hamburger_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #475569;
                border: none;
                font-size: 18px;
                font-weight: bold;
                min-width: 36px; min-height: 36px; max-width: 36px; max-height: 36px;
                border-radius: 8px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        layout.addWidget(self.hamburger_btn)

        # Blue Date badge
        today_num = str(datetime.date.today().day)
        self.cal_icon = QLabel(today_num)
        self.cal_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cal_icon.setFixedSize(28, 28)
        self.cal_icon.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3B82F6, stop:1 #1D4ED8);
            color: white;
            font-size: 13px;
            font-weight: 800;
            border-radius: 6px;
        """)
        layout.addWidget(self.cal_icon)

        # Title
        self.title_lbl = QLabel("Study Tasks")
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #0F172A; border: none; font-family: 'Inter', sans-serif;")
        layout.addWidget(self.title_lbl)

        layout.addSpacing(16)

        # Today Button
        self.today_btn = make_translatable(QPushButton(), "calendar.today")
        self.today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.today_btn.setStyleSheet("""
            QPushButton {
                background: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }
        """)
        layout.addWidget(self.today_btn)

        # Prev/Next navigation
        self.prev_btn = QPushButton("‹")
        self.next_btn = QPushButton("›")
        for btn in (self.prev_btn, self.next_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #475569; border: none; font-size: 18px; font-weight: bold; border-radius: 14px;
                    padding: 0px;
                }
                QPushButton:hover { background-color: #F1F5F9; color: #0F172A; }
            """)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)

        # Date range label
        self.date_label = QLabel("")
        self.date_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; font-family: 'Inter', sans-serif; border: none;")
        layout.addWidget(self.date_label)

        layout.addStretch()

        # ComboBox styles
        cb_style = """
            QComboBox {
                background: white; color: #0F172A; border: 1px solid #E2E8F0; padding: 6px 12px; border-radius: 6px; font-weight: 600;
            }
            QComboBox QAbstractItemView {
                background-color: white; color: #0F172A; selection-background-color: #F1F5F9; selection-color: #0F172A; border: 1px solid #E2E8F0;
            }
        """

        # Filters and Sort Dropdowns
        self.filter_cb = QComboBox()
        self.filter_cb.addItems([
            Translator.translate("calendar.all_tasks"),
            Translator.translate("calendar.only_manual"),
            Translator.translate("calendar.only_ai")
        ])
        self.filter_cb.setStyleSheet(cb_style)
        layout.addWidget(self.filter_cb)

        self.sort_cb = QComboBox()
        self.sort_cb.addItems([
            Translator.translate("calendar.sort_time"),
            Translator.translate("calendar.sort_duration")
        ])
        self.sort_cb.setStyleSheet(cb_style)
        layout.addWidget(self.sort_cb)

        # View Selector dropdown (Day, Week, Month, Year)
        self.view_cb = QComboBox()
        self.view_cb.addItems([
            Translator.translate("calendar.week"),
            Translator.translate("calendar.day"),
            Translator.translate("calendar.month"),
            Translator.translate("calendar.year")
        ])
        self.view_cb.setStyleSheet(cb_style)
        layout.addWidget(self.view_cb)

        # Add Button
        self.add_btn = make_translatable(QPushButton(), "button.add")
        self.add_btn.setText("+ " + Translator.translate("button.add"))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3B82F6, stop:1 #2563EB);
                color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 13px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563EB, stop:1 #1D4ED8);
            }
        """)
        layout.addWidget(self.add_btn)

    def retranslate_ui(self):
        super().retranslate_ui()
        self.title_lbl.setText(Translator.translate("nav.study_tasks"))
        
        # Reload combobox values without resetting selections
        curr_filt = self.filter_cb.currentIndex()
        self.filter_cb.clear()
        self.filter_cb.addItems([
            Translator.translate("calendar.all_tasks"),
            Translator.translate("calendar.only_manual"),
            Translator.translate("calendar.only_ai")
        ])
        self.filter_cb.setCurrentIndex(curr_filt)

        curr_sort = self.sort_cb.currentIndex()
        self.sort_cb.clear()
        self.sort_cb.addItems([
            Translator.translate("calendar.sort_time"),
            Translator.translate("calendar.sort_duration")
        ])
        self.sort_cb.setCurrentIndex(curr_sort)

        curr_view = self.view_cb.currentIndex()
        self.view_cb.clear()
        self.view_cb.addItems([
            Translator.translate("calendar.week"),
            Translator.translate("calendar.day"),
            Translator.translate("calendar.month"),
            Translator.translate("calendar.year")
        ])
        self.view_cb.setCurrentIndex(curr_view)


class ClassBlock(QFrame):
    clicked = pyqtSignal(dict, bool, QPoint) # block_data, is_ai, click_pos
    completed = pyqtSignal(dict, bool)

    def __init__(self, data, is_ai=False, parent=None):
        super().__init__(parent)
        self.data = data
        self.is_ai = is_ai
        
        title = data.get("title", "Study Block")
        block_type = data.get("type", "class") if not is_ai else "study_task"
        
        if is_ai:
            dur = data.get("duration_min", 60)
            subtitle = f"{dur} mins"
        else:
            room = data.get("room", "")
            group = data.get("group", "")
            subtitle = f"Room: {room}" if room else f"Group: {group}" if group else ""

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Harmonies palettes matching config
        colors = {
            "class": ("#F0F9FF", "#0284C7", "#38BDF8"),       # Blue
            "makeup": ("#FEF9C3", "#A16207", "#FBBF24"),      # Yellow
            "self_study": ("#FAF5FF", "#7E22CE", "#A855F7"),  # Purple
            "exam": ("#FEF2F2", "#B91C1C", "#F87171"),        # Red
            "study_task": ("#F0FDF4", "#15803D", "#4ADE80"),  # Green
            "other": ("#F8FAFC", "#475569", "#94A3B8")        # Gray
        }
        
        bg, text, border = colors.get(block_type, colors["other"])

        is_completed = data.get("completed", False)
        
        if is_completed:
            bg = "#F1F5F9"
            text = "#94A3B8"
            border = "#CBD5E1"
            decor = "line-through"
        else:
            decor = "none"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-left: 4px solid {border};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(1)

        hdr_lay = QHBoxLayout()
        hdr_lay.setContentsMargins(0, 0, 0, 0)

        # Category Badge
        badge_txt = block_type.replace("_", " ").title()
        badge = QLabel(badge_txt)
        badge.setStyleSheet(f"""
            color: {text}; font-size: 7px; font-weight: 800; text-transform: uppercase;
            border: 1px solid {border}; border-radius: 4px; padding: 1px 3px;
            background: rgba(255,255,255,0.7);
        """)
        hdr_lay.addWidget(badge)
        hdr_lay.addStretch()

        # Complete check indicator
        self.chk = QCheckBox()
        self.chk.setChecked(is_completed)
        self.chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 12px; height: 12px; border: 1px solid {border}; border-radius: 3px; background: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {border};
                image: url(resources/check.png); /* Fallback to standard check icon drawing */
            }}
        """)
        self.chk.clicked.connect(self._on_check_clicked)
        hdr_lay.addWidget(self.chk)
        layout.addLayout(hdr_lay)

        # Title
        t_lbl = QLabel(title)
        t_lbl.setWordWrap(True)
        t_lbl.setStyleSheet(f"color: {text}; font-size: 10px; font-weight: 700; border: none; text-decoration: {decor}; font-family: 'Inter';")
        layout.addWidget(t_lbl, 1)

        # Subtitle
        if subtitle:
            s_lbl = QLabel(subtitle)
            s_lbl.setWordWrap(True)
            s_lbl.setStyleSheet(f"color: {text}; font-size: 9px; border: none; text-decoration: {decor};")
            layout.addWidget(s_lbl)

    def mousePressEvent(self, event):
        # Prevent triggers when clicking checkboxes
        if not self.chk.geometry().contains(event.pos()):
            self.clicked.emit(self.data, self.is_ai, QCursor.pos())
        else:
            super().mousePressEvent(event)

    def _on_check_clicked(self):
        self.completed.emit(self.data, self.is_ai)


class SmartTaskPlanner(BaseTranslatableWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("SmartTaskPlanner")
        self.setStyleSheet("background-color: #F8FAFC;")

        self.base_date = datetime.date.today()
        self.current_view = "Week"
        
        # State: category checkboxes
        self.active_categories = {
            "class": True,
            "makeup": True,
            "self_study": True,
            "exam": True,
            "study_task": True,
            "other": True
        }

        # 1. Main Page Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 2. Resizable Sidebar & Content workspace
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E2E8F0;
                width: 1px;
            }
            QSplitter::handle:hover {
                background-color: #2563EB;
            }
        """)

        # LEFT SIDEBAR
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMinimumWidth(220)
        self.sidebar_widget.setMaximumWidth(320)
        self.sidebar_widget.setStyleSheet("background-color: #FFFFFF; border-right: 1px solid #E2E8F0;")
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(16, 16, 16, 16)
        self.sidebar_layout.setSpacing(24)

        # Mini calendar
        self.mini_cal = MiniMonthWidget(self.base_date.year, self.base_date.month, parent=self)
        self.mini_cal.month_clicked.connect(self.on_mini_cal_clicked)
        self.sidebar_layout.addWidget(self.mini_cal)

        # Category Filters Checkboxes Frame
        self.filters_frame = QFrame()
        self.filters_frame.setStyleSheet("background: transparent; border: none;")
        self.filters_layout = QVBoxLayout(self.filters_frame)
        self.filters_layout.setContentsMargins(0, 0, 0, 0)
        self.filters_layout.setSpacing(12)

        filter_hdr = QLabel("MY CALENDARS")
        filter_hdr.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748B; letter-spacing: 0.5px;")
        self.filters_layout.addWidget(filter_hdr)

        self.filter_checkboxes = {}
        colors_map = {
            "class": ("Class", "#0284C7"),
            "makeup": ("Makeup", "#A16207"),
            "self_study": ("Self Study", "#7E22CE"),
            "exam": ("Exam", "#B91C1C"),
            "study_task": ("Study Task (AI)", "#15803D"),
            "other": ("Other", "#475569")
        }

        for cat, (label, hex_color) in colors_map.items():
            chk = QCheckBox(label)
            chk.setChecked(True)
            chk.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 13px; font-weight: 500; color: #334155; spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 16px; height: 16px; border: 2px solid {hex_color}; border-radius: 4px; background: white;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {hex_color};
                    image: url(resources/check.png);
                }}
            """)
            chk.clicked.connect(lambda checked, c=cat: self.toggle_category(c))
            self.filters_layout.addWidget(chk)
            self.filter_checkboxes[cat] = chk

        self.sidebar_layout.addWidget(self.filters_frame)
        self.sidebar_layout.addStretch()

        self.splitter.addWidget(self.sidebar_widget)

        # RIGHT WORKSPACE
        self.workspace_container = QWidget()
        self.workspace_layout = QVBoxLayout(self.workspace_container)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(0)

        # Toolbar
        self.toolbar = PlannerToolbar()
        self.toolbar.hamburger_btn.clicked.connect(self.toggle_sidebar)
        self.toolbar.today_btn.clicked.connect(self.navigate_today)
        self.toolbar.prev_btn.clicked.connect(self.navigate_prev)
        self.toolbar.next_btn.clicked.connect(self.navigate_next)
        self.toolbar.add_btn.clicked.connect(self._add_class)
        self.toolbar.view_cb.currentIndexChanged.connect(self.on_view_changed)
        self.toolbar.filter_cb.currentIndexChanged.connect(self.refresh)
        self.toolbar.sort_cb.currentIndexChanged.connect(self.refresh)
        self.workspace_layout.addWidget(self.toolbar)

        # Scroll Workspace
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background-color: #FFFFFF; }")

        self.grid_container = CalendarGridContainer()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setSpacing(0) # Google calendar grids have zero margins between cell splits

        self.scroll.setWidget(self.grid_container)
        self.workspace_layout.addWidget(self.scroll, 1)

        self.splitter.addWidget(self.workspace_container)
        
        # Lock splitter sizes initially to give sidebar 240px
        self.splitter.setSizes([240, 1110])

        self.main_layout.addWidget(self.splitter)

        # Refresh Timer for red horizontal line
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_current_time_indicators)
        self.refresh_timer.start(60000) # update every 60s

        self.refresh()

    def toggle_sidebar(self):
        self.sidebar_widget.setHidden(not self.sidebar_widget.isHidden())

    def toggle_category(self, category):
        self.active_categories[category] = self.filter_checkboxes[category].isChecked()
        self.refresh()

    def on_view_changed(self, index):
        views = ["Week", "Day", "Month", "Year"]
        self.current_view = views[index]
        self.refresh()

    def on_mini_cal_clicked(self, date):
        self.base_date = date
        self.refresh()

    def on_year_date_clicked(self, date):
        self.base_date = date
        self.current_view = "Day"
        self.toolbar.view_cb.setCurrentIndex(1)
        self.refresh()

    def _on_month_cell_clicked(self, date_val, click_pos):
        self.base_date = date_val
        
        # Map the clicked date's weekday to weekday name string
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_name = days_of_week[date_val.weekday()]
        
        data = {
            "title": "",
            "day": weekday_name,
            "period_start": 7,
            "period_end": 7,
            "type": "class",
            "room": "",
            "group": ""
        }
        dialog = QuickCreateDialog(data=data, is_ai=False, click_position=click_pos, parent=self)
        res = dialog.exec()
        if res == 10:
            partial = dialog.get_data()
            full_dialog = FullEventDialog(data=partial, click_position=click_pos, parent=self)
            if full_dialog.exec():
                new_data = full_dialog.get_data()
                self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))
        elif res == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))

    def _on_month_cell_double_clicked(self, date_val):
        self.base_date = date_val
        self.current_view = "Day"
        self.toolbar.view_cb.setCurrentIndex(1)
        self.refresh()

    def navigate_today(self):
        self.base_date = datetime.date.today()
        self.refresh()

    def navigate_prev(self):
        if self.current_view == "Day":
            self.base_date -= datetime.timedelta(days=1)
        elif self.current_view == "Week":
            self.base_date -= datetime.timedelta(days=7)
        elif self.current_view == "Month":
            y, m = self.base_date.year, self.base_date.month - 1
            if m == 0:
                m = 12
                y -= 1
            self.base_date = datetime.date(y, m, 1)
        elif self.current_view == "Year":
            self.base_date = datetime.date(self.base_date.year - 1, self.base_date.month, 1)
        self.refresh()

    def navigate_next(self):
        if self.current_view == "Day":
            self.base_date += datetime.timedelta(days=1)
        elif self.current_view == "Week":
            self.base_date += datetime.timedelta(days=7)
        elif self.current_view == "Month":
            y, m = self.base_date.year, self.base_date.month + 1
            if m == 13:
                m = 1
                y += 1
            self.base_date = datetime.date(y, m, 1)
        elif self.current_view == "Year":
            self.base_date = datetime.date(self.base_date.year + 1, self.base_date.month, 1)
        self.refresh()

    def update_current_time_indicators(self):
        if self.current_view in ["Day", "Week"]:
            for i in range(self.grid_layout.count()):
                item = self.grid_layout.itemAt(i)
                if item and item.widget():
                    w = item.widget()
                    if isinstance(w, ClickableCell):
                        w.update()

    def _add_class(self):
        click_pos = QCursor.pos()
        # Initialize with today's day of week
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day = days_of_week[self.base_date.weekday()]
        data = {
            "title": "",
            "day": current_day,
            "period_start": 7,
            "period_end": 7,
            "type": "class",
            "room": "",
            "group": ""
        }
        
        dialog = QuickCreateDialog(data=data, is_ai=False, click_position=click_pos, parent=self)
        res = dialog.exec()
        if res == 10: # More Options clicked
            partial = dialog.get_data()
            full_dialog = FullEventDialog(data=partial, click_position=click_pos, parent=self)
            if full_dialog.exec():
                new_data = full_dialog.get_data()
                self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))
        elif res == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))

    def _on_cell_clicked(self, day, period, click_pos):
        data = {
            "title": "",
            "day": day,
            "period_start": period,
            "period_end": period,
            "type": "class",
            "room": "",
            "group": ""
        }
        dialog = QuickCreateDialog(data=data, is_ai=False, click_position=click_pos, parent=self)
        res = dialog.exec()
        if res == 10:
            partial = dialog.get_data()
            full_dialog = FullEventDialog(data=partial, click_position=click_pos, parent=self)
            if full_dialog.exec():
                new_data = full_dialog.get_data()
                self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))
        elif res == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            self._update_sqlite(new_data, action="add", is_ai=(new_data.get("type") == "study_task"))

    def _on_block_clicked(self, block_data, is_ai, click_pos):
        dialog = QuickCreateDialog(data=block_data, is_ai=is_ai, click_position=click_pos, parent=self)
        res = dialog.exec()
        if res == 10:
            partial = dialog.get_data()
            full_dialog = FullEventDialog(data=partial, is_ai=is_ai, click_position=click_pos, parent=self)
            f_res = full_dialog.exec()
            if f_res == QDialog.DialogCode.Accepted:
                if full_dialog.action == "save":
                    new_data = full_dialog.get_data()
                    self._update_sqlite(block_data, action="edit", new_data=new_data, is_ai=is_ai)
                elif full_dialog.action == "delete":
                    self._update_sqlite(block_data, action="delete", is_ai=is_ai)
                elif full_dialog.action == "assign":
                    new_data = full_dialog.get_data()
                    # Delete AI study task and assign to manual schedule
                    self._update_sqlite(block_data, action="delete", is_ai=True)
                    self._update_sqlite(new_data, action="add", is_ai=False)
        elif res == QDialog.DialogCode.Accepted:
            if dialog.action == "save":
                new_data = dialog.get_data()
                self._update_sqlite(block_data, action="edit", new_data=new_data, is_ai=is_ai)
            elif dialog.action == "delete":
                self._update_sqlite(block_data, action="delete", is_ai=is_ai)
            elif dialog.action == "assign":
                new_data = dialog.get_data()
                self._update_sqlite(block_data, action="delete", is_ai=True)
                self._update_sqlite(new_data, action="add", is_ai=False)

    def _complete_class(self, block_data, is_ai):
        self._update_sqlite(block_data, action="complete", is_ai=is_ai)

    def _update_sqlite(self, target_data, action="add", new_data=None, is_ai=False):
        student = crud.get_current_student()
        if not student: return

        context = student.get("context", {})
        raw_input = context.get("raw_input", {})
        ai_plan = context.get("ai_plan", {})

        if not isinstance(raw_input, dict): raw_input = {}
        if not isinstance(raw_input.get("academic_context"), dict):
            raw_input["academic_context"] = {}
        timetable = raw_input["academic_context"].get("timetable_manual", [])
        if not isinstance(timetable, list): timetable = []

        if not is_ai:
            if action == "add":
                timetable.append(target_data)
            elif action == "delete":
                for item in list(timetable):
                    if item.get("title") == target_data.get("title") and item.get("day") == target_data.get("day") and item.get("period_start") == target_data.get("period_start"):
                        timetable.remove(item)
            elif action == "complete":
                for t in timetable:
                    if t.get("title") == target_data.get("title") and t.get("day") == target_data.get("day") and t.get("period_start") == target_data.get("period_start"):
                        t["completed"] = not t.get("completed", False)
                        break
            elif action == "edit":
                for idx, item in enumerate(timetable):
                    if item.get("title") == target_data.get("title") and item.get("day") == target_data.get("day") and item.get("period_start") == target_data.get("period_start"):
                        timetable[idx] = new_data
                        break
            raw_input["academic_context"]["timetable_manual"] = timetable
        else:
            weekly_plan = ai_plan.get("weekly_study_plan", [])
            if not isinstance(weekly_plan, list):
                weekly_plan = []
            
            if action == "add":
                # Find or create day_plan
                day_plan = None
                for dp in weekly_plan:
                    if dp.get("day") == target_data.get("day"):
                        day_plan = dp
                        break
                if not day_plan:
                    day_plan = {"day": target_data.get("day"), "tasks": []}
                    weekly_plan.append(day_plan)
                day_plan.setdefault("tasks", []).append(target_data)
            elif action == "delete":
                for dp in weekly_plan:
                    tasks = dp.get("tasks", [])
                    for t in list(tasks):
                        if t.get("title") == target_data.get("title"):
                            tasks.remove(t)
            elif action == "complete":
                for dp in weekly_plan:
                    tasks = dp.get("tasks", [])
                    for t in tasks:
                        if t.get("title") == target_data.get("title"):
                            t["completed"] = not t.get("completed", False)
                            break
            elif action == "edit":
                for dp in weekly_plan:
                    tasks = dp.get("tasks", [])
                    for idx, t in enumerate(tasks):
                        if t.get("title") == target_data.get("title"):
                            tasks[idx]["title"] = new_data["title"]
                            if "duration_min" in new_data:
                                tasks[idx]["duration_min"] = new_data["duration_min"]
                            break
            ai_plan["weekly_study_plan"] = weekly_plan

        crud.save_student_context(
            student_id=student["id"],
            raw_input_dict=raw_input,
            ai_plan_dict=ai_plan,
            ai_status=context.get("ai_status", "COMPLETED"),
            ai_last_error=context.get("ai_last_error"),
            is_dirty=1
        )
        self.refresh()

    def refresh(self):
        # 1. Clear current grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Update mini calendar date to sync month view
        if self.mini_cal.year != self.base_date.year or self.mini_cal.month != self.base_date.month:
            self.mini_cal.year = self.base_date.year
            self.mini_cal.month = self.base_date.month
            self.mini_cal.hdr_lbl.setText(datetime.date(self.base_date.year, self.base_date.month, 1).strftime("%B %Y"))
            self.mini_cal.populate_days()

        # 2. Route views
        if self.current_view == "Day":
            self.refresh_day_view()
        elif self.current_view == "Week":
            self.refresh_week_view()
        elif self.current_view == "Month":
            self.refresh_month_view()
        elif self.current_view == "Year":
            self.refresh_year_view()

    def _get_student_data(self):
        student = crud.get_current_student()
        if not student:
            return [], []
            
        context = student.get("context", {})
        raw_input = context.get("raw_input", {})
        if not isinstance(raw_input, dict): raw_input = {}
        timetable_manual = raw_input.get("academic_context", {}).get("timetable_manual", []) if isinstance(raw_input.get("academic_context"), dict) else []
        
        ai_plan = context.get("ai_plan", {})
        if not isinstance(ai_plan, dict): ai_plan = {}
        weekly_plan = ai_plan.get("weekly_study_plan", [])
        
        # Parse AI study tasks
        ai_tasks = []
        if isinstance(weekly_plan, list):
            for day_plan in weekly_plan:
                if isinstance(day_plan, dict):
                    day = day_plan.get("day")
                    tasks = day_plan.get("tasks", [])
                    for t in tasks:
                        if isinstance(t, dict):
                            t_copy = t.copy()
                            t_copy["day"] = day
                            # AI tasks are periodized or timed. Map them to periods or specific days
                            ai_tasks.append(t_copy)
                            
        # Filter categories based on checkbox settings
        filtered_manual = []
        for event in timetable_manual:
            cat = event.get("type", "class")
            if self.active_categories.get(cat, True):
                filtered_manual.append(event)
                
        filtered_ai = []
        for t in ai_tasks:
            cat = t.get("type", "study_task")
            if self.active_categories.get(cat, True):
                filtered_ai.append(t)
                
        # Dropdowns checks
        f_idx = self.toolbar.filter_cb.currentIndex()
        show_manual = f_idx in [0, 1]
        show_ai = f_idx in [0, 2]
        
        manual_to_show = filtered_manual if show_manual else []
        ai_to_show = filtered_ai if show_ai else []
        
        # Sort AI tasks if required
        sort_idx = self.toolbar.sort_cb.currentIndex()
        if sort_idx == 1:
            ai_to_show.sort(key=lambda x: int(x.get("duration_min", 0)), reverse=True)
            
        return manual_to_show, ai_to_show

    def refresh_day_view(self):
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today_wday = days_of_week[self.base_date.weekday()]
        
        self.toolbar.date_label.setText(self.base_date.strftime("%B %d, %Y"))

        # Row 0: Corner Label (empty)
        corner_widget = QWidget()
        corner_widget.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.grid_layout.addWidget(corner_widget, 0, 0)

        # Row 0: Header for the active day
        is_today = (self.base_date == datetime.date.today())
        hdr = DayHeaderWidget(today_wday, self.base_date, is_today=is_today, parent=self)
        self.grid_layout.addWidget(hdr, 0, 1)
        self.grid_layout.setColumnStretch(1, 1)

        # Row 1: GMT+07 Corner
        gmt_lbl = QLabel("GMT+07")
        gmt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gmt_lbl.setStyleSheet("color: #64748B; font-weight: 700; font-size: 10px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; background: #FFFFFF; padding: 4px;")
        self.grid_layout.addWidget(gmt_lbl, 1, 0)

        # Row 1: All-day Cell
        manual_events, ai_events = self._get_student_data()
        day_manual = [b for b in manual_events if b.get("day") == today_wday]
        day_ai = [t for t in ai_events if t.get("day") == today_wday]
        pending_count = sum(1 for b in day_manual if not b.get("completed", False)) + \
                        sum(1 for t in day_ai if not t.get("completed", False))
        
        all_day_cell = AllDayCell(today_wday, parent=self)
        if pending_count > 0:
            pill = PendingTasksPill(pending_count)
            all_day_cell.layout.addWidget(pill)
        self.grid_layout.addWidget(all_day_cell, 1, 1)

        # Row 2+: Hours
        hours_times = []
        for h in range(24):
            if h == 0:
                t_str = "12 AM"
            elif h < 12:
                t_str = f"{h} AM"
            elif h == 12:
                t_str = "12 PM"
            else:
                t_str = f"{h-12} PM"
            hours_times.append((h, t_str))

        for idx, (h, t_str) in enumerate(hours_times):
            p_lbl = QLabel(t_str)
            p_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            p_lbl.setStyleSheet("""
                QLabel {
                    color: #64748B;
                    font-size: 11px;
                    font-weight: 600;
                    border-right: 1px solid #E2E8F0;
                    padding-right: 8px;
                    padding-top: 4px;
                    background: transparent;
                }
            """)
            p_lbl.setFixedWidth(64)
            self.grid_layout.addWidget(p_lbl, h + 2, 0)
            self.grid_layout.setRowMinimumHeight(h + 2, 60)
            
            # Clickable cell
            cell = ClickableCell(today_wday, h, parent=self)
            cell.clicked.connect(self._on_cell_clicked)
            self.grid_layout.addWidget(cell, h + 2, 1)

        # Render manual timetable events
        for block in manual_events:
            if block.get("day") == today_wday:
                p_start = max(0, min(23, int(block.get("period_start", 7))))
                p_end = max(0, min(23, int(block.get("period_end", 7))))
                if p_start > p_end: p_start, p_end = p_end, p_start
                span = p_end - p_start + 1

                cb = ClassBlock(block, is_ai=False, parent=self)
                cb.clicked.connect(self._on_block_clicked)
                cb.completed.connect(self._complete_class)
                self.grid_layout.addWidget(cb, p_start + 2, 1, span, 1)

        # Render AI events
        free_periods = [p for p in range(24) if not any(int(b.get("period_start", 0)) <= p <= int(b.get("period_end", 0)) for b in manual_events if b.get("day") == today_wday)]
        for t in ai_events:
            if t.get("day") == today_wday:
                if free_periods:
                    target_p = free_periods.pop(0)
                    cb = ClassBlock(t, is_ai=True, parent=self)
                    cb.clicked.connect(self._on_block_clicked)
                    cb.completed.connect(self._complete_class)
                    self.grid_layout.addWidget(cb, target_p + 2, 1, 1, 1)
                else:
                    cb = ClassBlock(t, is_ai=True, parent=self)
                    cb.clicked.connect(self._on_block_clicked)
                    cb.completed.connect(self._complete_class)
                    self.grid_layout.addWidget(cb, 23 + 2, 1, 1, 1)

    def refresh_week_view(self):
        # Calculate dates of active week
        start_date = self.base_date - datetime.timedelta(days=self.base_date.weekday())
        week_dates = [start_date + datetime.timedelta(days=i) for i in range(7)]
        
        end_date = week_dates[-1]
        
        self.toolbar.date_label.setText(f"{start_date.strftime('%B %d')} – {end_date.strftime('%B %d, %Y')}")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Row 0: Corner Label (empty)
        corner_widget = QWidget()
        corner_widget.setStyleSheet("background-color: #FFFFFF; border: none;")
        self.grid_layout.addWidget(corner_widget, 0, 0)

        # Row 0: Columns Headers
        for col_idx, day_name in enumerate(days):
            date_val = week_dates[col_idx]
            is_today = (date_val == datetime.date.today())
            hdr = DayHeaderWidget(day_name, date_val, is_today=is_today, parent=self)
            self.grid_layout.addWidget(hdr, 0, col_idx + 1)
            self.grid_layout.setColumnStretch(col_idx + 1, 1)

        # Row 1: GMT+07 Corner
        gmt_lbl = QLabel("GMT+07")
        gmt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gmt_lbl.setStyleSheet("color: #64748B; font-weight: 700; font-size: 10px; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; background: #FFFFFF; padding: 4px;")
        self.grid_layout.addWidget(gmt_lbl, 1, 0)

        # Load events
        manual_events, ai_events = self._get_student_data()

        # Row 1: All-day Row for columns 1 to 7
        for col_idx, day_name in enumerate(days):
            day_manual = [b for b in manual_events if b.get("day") == day_name]
            day_ai = [t for t in ai_events if t.get("day") == day_name]
            pending_count = sum(1 for b in day_manual if not b.get("completed", False)) + \
                            sum(1 for t in day_ai if not t.get("completed", False))
            
            all_day_cell = AllDayCell(day_name, parent=self)
            if pending_count > 0:
                pill = PendingTasksPill(pending_count)
                all_day_cell.layout.addWidget(pill)
            self.grid_layout.addWidget(all_day_cell, 1, col_idx + 1)

        # Row 2+: Hours (24 hours)
        hours_times = []
        for h in range(24):
            if h == 0:
                t_str = "12 AM"
            elif h < 12:
                t_str = f"{h} AM"
            elif h == 12:
                t_str = "12 PM"
            else:
                t_str = f"{h-12} PM"
            hours_times.append((h, t_str))

        for idx, (h, t_str) in enumerate(hours_times):
            p_lbl = QLabel(t_str)
            p_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            p_lbl.setStyleSheet("""
                QLabel {
                    color: #64748B;
                    font-size: 11px;
                    font-weight: 600;
                    border-right: 1px solid #E2E8F0;
                    padding-right: 8px;
                    padding-top: 4px;
                    background: transparent;
                }
            """)
            p_lbl.setFixedWidth(64)
            self.grid_layout.addWidget(p_lbl, h + 2, 0)
            self.grid_layout.setRowMinimumHeight(h + 2, 60)
            
            for col_idx, day_name in enumerate(days):
                cell = ClickableCell(day_name, h, parent=self)
                cell.clicked.connect(self._on_cell_clicked)
                self.grid_layout.addWidget(cell, h + 2, col_idx + 1)

        # Render Manual
        for block in manual_events:
            day = block.get("day")
            if day in days:
                col = days.index(day) + 1
                p_start = max(0, min(23, int(block.get("period_start", 7))))
                p_end = max(0, min(23, int(block.get("period_end", 7))))
                if p_start > p_end: p_start, p_end = p_end, p_start
                span = p_end - p_start + 1

                cb = ClassBlock(block, is_ai=False, parent=self)
                cb.clicked.connect(self._on_block_clicked)
                cb.completed.connect(self._complete_class)
                self.grid_layout.addWidget(cb, p_start + 2, col, span, 1)

        # Render AI Study Tasks on free slots
        for day in days:
            col = days.index(day) + 1
            day_manual = [b for b in manual_events if b.get("day") == day]
            free_periods = [p for p in range(24) if not any(int(b.get("period_start", 0)) <= p <= int(b.get("period_end", 0)) for b in day_manual)]
            day_ai = [t for t in ai_events if t.get("day") == day]
            
            for t in day_ai:
                if free_periods:
                    target_p = free_periods.pop(0)
                    cb = ClassBlock(t, is_ai=True, parent=self)
                    cb.clicked.connect(self._on_block_clicked)
                    cb.completed.connect(self._complete_class)
                    self.grid_layout.addWidget(cb, target_p + 2, col, 1, 1)
                else:
                    cb = ClassBlock(t, is_ai=True, parent=self)
                    cb.clicked.connect(self._on_block_clicked)
                    cb.completed.connect(self._complete_class)
                    self.grid_layout.addWidget(cb, 23 + 2, col, 1, 1)

    def refresh_month_view(self):
        self.toolbar.date_label.setText(self.base_date.strftime("%B %Y"))

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Weekdays headers
        for col, day_name in enumerate(days):
            lbl = QLabel(day_name[:3].upper())
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #475569; font-weight: bold; font-size: 11px; padding: 5px; border-bottom: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0;")
            self.grid_layout.addWidget(lbl, 0, col)
            self.grid_layout.setColumnStretch(col, 1)

        # Calendar generation
        cal = calendar.Calendar(firstweekday=0)
        month_days = list(cal.itermonthdays4(self.base_date.year, self.base_date.month))
        
        # Load events
        manual_events, ai_events = self._get_student_data()
        
        today = datetime.date.today()
        row = 1
        col = 0
        
        for year_val, month_val, day_val, weekday_idx in month_days:
            # We only show weeks that have at least some days in this month
            if month_val != self.base_date.month and row > 4 and col == 0:
                break
                
            is_curr_month = (month_val == self.base_date.month)
            cell = ClickableMonthCell(datetime.date(year_val, month_val, day_val), is_curr_month, parent=self)
            cell.clicked.connect(self._on_month_cell_clicked)
            cell.double_clicked.connect(self._on_month_cell_double_clicked)
            cell_lay = QVBoxLayout(cell)
            cell_lay.setContentsMargins(4, 4, 4, 4)
            cell_lay.setSpacing(4)

            # Date number badge
            num_lay = QHBoxLayout()
            num_lay.setContentsMargins(0, 0, 0, 0)
            
            lbl_num = QLabel(str(day_val))
            if datetime.date(year_val, month_val, day_val) == today:
                lbl_num.setStyleSheet("""
                    color: white; background-color: #2563EB; font-weight: bold;
                    border-radius: 9px; min-width: 18px; max-width: 18px;
                    min-height: 18px; max-height: 18px; text-align: center;
                    font-size: 11px; padding: 1px;
                """)
                lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif month_val != self.base_date.month:
                lbl_num.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 500;")
            else:
                lbl_num.setStyleSheet("color: #0F172A; font-size: 11px; font-weight: 600;")
            
            num_lay.addWidget(lbl_num)
            num_lay.addStretch()
            cell_lay.addLayout(num_lay)

            # Render compact daily tasks inside month cells
            day_name = days[weekday_idx]
            day_manual = [b for b in manual_events if b.get("day") == day_name]
            day_ai = [t for t in ai_events if t.get("day") == day_name]
            
            # Combine & limit to max 3 items to fit month views
            combined = [(b, False) for b in day_manual] + [(t, True) for t in day_ai]
            for item, is_ai in combined[:3]:
                t_lbl = QPushButton(item.get("title", "Task"))
                t_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
                
                # Category specific colors
                type_colors = {
                    "class": ("#0284C7", "#E0F2FE"),
                    "study_task": ("#15803D", "#DCFCE7"),
                    "exam": ("#B91C1C", "#FEE2E2"),
                    "other": ("#475569", "#F1F5F9")
                }
                fg, bg_col = type_colors.get(item.get("type", "study_task" if is_ai else "class"), type_colors["other"])
                
                t_lbl.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg_col};
                        color: {fg};
                        border: none;
                        border-radius: 3px;
                        font-size: 10px;
                        font-weight: bold;
                        padding: 2px 4px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: #CBD5E1;
                    }}
                """)
                
                # Setup click connection
                click_pos = QCursor.pos()
                t_lbl.clicked.connect(lambda checked, i=item, ia=is_ai, p=click_pos: self._on_block_clicked(i, ia, p))
                cell_lay.addWidget(t_lbl)

            cell_lay.addStretch()
            self.grid_layout.addWidget(cell, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def refresh_year_view(self):
        year = self.base_date.year
        self.toolbar.date_label.setText(str(year))
        
        row, col = 0, 0
        for m in range(1, 13):
            cal_card = QFrame()
            cal_card.setObjectName("YearCalCard")
            cal_card.setStyleSheet("""
                #YearCalCard {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                    padding: 8px;
                }
                #YearCalCard:hover {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                }
            """)
            shadow = QGraphicsDropShadowEffect(cal_card)
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(15, 23, 42, 15))
            shadow.setOffset(0, 3)
            cal_card.setGraphicsEffect(shadow)
            
            card_lay = QVBoxLayout(cal_card)
            card_lay.setContentsMargins(0, 0, 0, 0)
            
            widget = MiniMonthWidget(year, m, parent=self)
            widget.month_clicked.connect(self.on_year_date_clicked)
            card_lay.addWidget(widget)
            
            self.grid_layout.addWidget(cal_card, row, col)
            self.grid_layout.setColumnStretch(col, 1)
            self.grid_layout.setRowMinimumHeight(row, 160)
            self.grid_layout.setRowStretch(row, 1)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

    def retranslate_ui(self):
        super().retranslate_ui()
        self.toolbar.retranslate_ui()
        self.refresh()
