import sys
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QLineEdit, QTextEdit, QComboBox, QMessageBox,
                             QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,
                             QTabWidget, QSpinBox, QInputDialog, QSplitter)
from PyQt6.QtCore import Qt, QSize, QRectF, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QCursor, QFont, QLinearGradient, QIcon

from core.config import *
from ui_core.components import SaaSCard, AnimatedCircularProgress, AnimatedProgressBar, AnimationEngine, CollapsiblePanel
from core.i18n import _
from database import crud

class ShadowCard(QFrame):
    def __init__(self, parent=None, radius=20):
        super().__init__(parent)
        self.setObjectName("ShadowCard")
        self.setStyleSheet(f"""
            #ShadowCard {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: {radius}px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(18, 55, 105, 20))
        self.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

class SkillChip(QWidget):
    def __init__(self, name, level="Advanced"):
        super().__init__()
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        self.setStyleSheet(f"""
            QWidget {{
                background: #F1F5F9;
                border-radius: 16px;
            }}
        """)
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: #0F172A; font-weight: 600; font-size: 13px;")
        
        dot = QWidget()
        dot.setFixedSize(6, 6)
        dot_color = "#38BDF8" if level == "Advanced" else "#94A3B8"
        dot.setStyleSheet(f"background: {dot_color}; border-radius: 3px;")
        
        level_lbl = QLabel(level)
        level_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        
        layout.addWidget(name_lbl)
        layout.addWidget(dot)
        layout.addWidget(level_lbl)

class ProjectCard(ShadowCard):
    def __init__(self, title, tags, description="Modern AI-driven platform for enterprise solutions."):
        super().__init__(radius=20)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        thumb = QFrame()
        thumb.setFixedHeight(140)
        thumb.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F1F5F9, stop:1 #E2E8F0);
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        """)
        self.layout.addWidget(thumb)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 20)
        content_layout.setSpacing(12)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        content_layout.addWidget(title_lbl)
        
        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #64748B; font-size: 13px; line-height: 1.4;")
        content_layout.addWidget(desc_lbl)
        
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        for tag in tags:
            t_lbl = QLabel(tag)
            t_lbl.setStyleSheet("background: #F0F9FF; color: #0369A1; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;")
            tags_layout.addWidget(t_lbl)
        tags_layout.addStretch()
        content_layout.addLayout(tags_layout)
        
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(12)
        
        gh_btn = QPushButton("View Material")
        gh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gh_btn.setStyleSheet("background: #0F172A; color: white; border-radius: 8px; height: 32px; font-weight: 600; font-size: 12px; padding: 0 12px;")
        
        demo_btn = QPushButton("Syllabus")
        demo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        demo_btn.setStyleSheet("background: white; color: #0F172A; border: 1px solid #E2E8F0; border-radius: 8px; height: 32px; font-weight: 600; font-size: 12px; padding: 0 12px;")
        
        btns_layout.addWidget(gh_btn)
        btns_layout.addWidget(demo_btn)
        btns_layout.addStretch()
        content_layout.addLayout(btns_layout)
        
        self.layout.addWidget(content)

class TimelineItem(QWidget):
    def __init__(self, title, subtitle, date, is_last=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 4, 0, 0)
        dot = QWidget()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet("background: #38BDF8; border: 3px solid #E0F2FE; border-radius: 6px;")
        left_col.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        if not is_last:
            line = QFrame()
            line.setFixedWidth(2)
            line.setStyleSheet("background: #E2E8F0; margin-top: 4px; margin-bottom: 4px;")
            left_col.addWidget(line, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            left_col.addStretch(1)
            
        layout.addLayout(left_col)
        
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")
        
        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        
        d_lbl = QLabel(date)
        d_lbl.setStyleSheet("color: #94A3B8; font-size: 12px; font-weight: 500;")
        
        right_col.addWidget(t_lbl)
        right_col.addWidget(s_lbl)
        right_col.addWidget(d_lbl)
        right_col.addSpacing(16)
        
        layout.addLayout(right_col, 1)

class TimetableEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        self.rows_layout = QVBoxLayout()
        self.layout.addLayout(self.rows_layout)
        
        add_btn = QPushButton("+ Add Class")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("background: #38BDF8; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        add_btn.clicked.connect(lambda: self.add_row())
        self.layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.rows = []

    def add_row(self, data=None):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)
        
        day_cb = QComboBox()
        day_cb.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        start_cb = QComboBox()
        start_cb.addItems([str(i) for i in range(1, 11)])
        end_cb = QComboBox()
        end_cb.addItems([str(i) for i in range(1, 11)])
        
        title_le = QLineEdit()
        title_le.setPlaceholderText("Title")
        group_le = QLineEdit()
        group_le.setPlaceholderText("Group")
        group_le.setFixedWidth(60)
        room_le = QLineEdit()
        room_le.setPlaceholderText("Room")
        room_le.setFixedWidth(60)
        
        type_cb = QComboBox()
        type_cb.addItems(["class", "makeup", "self_study", "exam", "other"])
        
        del_btn = QPushButton("X")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("background: #EF4444; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold;")
        del_btn.clicked.connect(lambda: self.remove_row(row_widget))
        
        row_layout.addWidget(day_cb)
        row_layout.addWidget(QLabel("Tiết:"))
        row_layout.addWidget(start_cb)
        row_layout.addWidget(QLabel("-"))
        row_layout.addWidget(end_cb)
        row_layout.addWidget(title_le)
        row_layout.addWidget(group_le)
        row_layout.addWidget(room_le)
        row_layout.addWidget(type_cb)
        row_layout.addWidget(del_btn)
        
        if data:
            day_cb.setCurrentText(data.get("day", "Monday"))
            start_cb.setCurrentText(str(data.get("period_start", 1)))
            end_cb.setCurrentText(str(data.get("period_end", 4)))
            title_le.setText(data.get("title", ""))
            group_le.setText(data.get("group", ""))
            room_le.setText(data.get("room", ""))
            type_cb.setCurrentText(data.get("type", "class"))
            
        self.rows_layout.addWidget(row_widget)
        self.rows.append({
            "widget": row_widget,
            "day": day_cb, "start": start_cb, "end": end_cb,
            "title": title_le, "group": group_le, "room": room_le, "type": type_cb
        })

    def remove_row(self, widget):
        for row in self.rows:
            if row["widget"] == widget:
                self.rows.remove(row)
                widget.deleteLater()
                break

    def get_data(self):
        data = []
        for row in self.rows:
            title = row["title"].text().strip()
            if not title:
                continue
            data.append({
                "day": row["day"].currentText(),
                "period_start": int(row["start"].currentText()),
                "period_end": int(row["end"].currentText()),
                "title": title,
                "group": row["group"].text().strip(),
                "room": row["room"].text().strip(),
                "type": row["type"].currentText()
            })
        return data

    def clear(self):
        for row in self.rows:
            row["widget"].deleteLater()
        self.rows.clear()

class ProfilePage(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("ProfilePage")
        self.setStyleSheet("background-color: #F8FAFC;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.init_toolbar()
        
        content_container = QWidget()
        self.content_layout = QHBoxLayout(content_container)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(16)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: transparent;
                color: #64748B;
                font-weight: 600;
                font-size: 14px;
                padding: 12px 24px;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #0F172A;
                border-bottom: 2px solid #38BDF8;
                font-weight: 700;
            }
            QTabBar::tab:hover {
                color: #0F172A;
            }
        """)
        
        # 1. Tab 1: Academic Profile Form
        self.form_tab = QWidget()
        self.init_form_tab()
        self.tabs.addTab(self.form_tab, "Academic Profile Form")
        
        # 2. Tab 2: Portfolio View (Scrollable workspace)
        self.portfolio_tab = QWidget()
        self.init_portfolio_tab()
        self.tabs.addTab(self.portfolio_tab, "AI Academic Plan")
        
        # 3. Tab 3: GPA Manager
        self.gpa_tab = QWidget()
        self.init_gpa_tab()
        self.tabs.addTab(self.gpa_tab, "GPA Manager")
        
        self.profile_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.profile_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E2E8F0;
                width: 4px;
                margin: 0 8px;
            }
            QSplitter::handle:hover {
                background-color: #2563EB;
            }
        """)
        
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.profile_splitter.addWidget(self.tabs)
        
        # 3. Right Insights Panel
        self.insights_content = self._setup_insights_panel()
        self.insights_content.setMinimumWidth(300)
        self.profile_splitter.addWidget(self.insights_content)
        self.profile_splitter.setSizes([750, 300])
        
        self.content_layout.addWidget(self.profile_splitter, 1)
        
        self.main_layout.addWidget(content_container, 1)
        
        self.refresh()

    def init_toolbar(self):
        toolbar = QWidget()
        toolbar.setFixedHeight(80)
        toolbar.setStyleSheet("background: white; border-bottom: 1px solid #E2E8F0;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)
        
        breadcrumbs = QLabel("AI Academic Plan")
        breadcrumbs.setStyleSheet("color: #64748B; font-weight: 600; font-size: 14px;")
        layout.addWidget(breadcrumbs)
        
        layout.addStretch()
        
        edit_btn = QPushButton("Academic Form")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #E2E8F0; border-radius: 10px;
                color: #0F172A; font-weight: 700; font-size: 13px; height: 40px; padding: 0 16px;
            }
            QPushButton:hover { background: #F8FAFC; }
        """)
        edit_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        
        export_btn = QPushButton("View Plan")
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #0F172A; border-radius: 10px;
                color: white; font-weight: 700; font-size: 13px; height: 40px; padding: 0 16px;
            }
            QPushButton:hover { background: #1E293B; }
        """)
        export_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        
        layout.addWidget(edit_btn)
        layout.addWidget(export_btn)
        
        self.mini_avatar = QLabel()
        self.mini_avatar.setFixedSize(40, 40)
        self.mini_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mini_avatar.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38BDF8, stop:1 #0284C7);
            color: white;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        """)
        layout.addWidget(self.mini_avatar)
        
        self.main_layout.addWidget(toolbar)

    def init_form_tab(self):
        layout = QVBoxLayout(self.form_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setFrameShape(QFrame.Shape.NoFrame)
        form_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        form_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(24)
        
        self.form_card = ShadowCard(radius=24)
        self.form_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        fc_layout = self.form_card.layout
        
        form_title = QLabel("Edit Academic Profile")
        form_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #0F172A;")
        fc_layout.addWidget(form_title)
        
        def create_group(title):
            group = QFrame()
            group.setStyleSheet("""
                QFrame {
                    background: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                }
            """)
            layout = QVBoxLayout(group)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(16)
            
            lbl = QLabel(title)
            lbl.setStyleSheet("color: #0F172A; font-size: 16px; font-weight: 700; border: none;")
            layout.addWidget(lbl)
            
            grid = QGridLayout()
            grid.setSpacing(12)
            grid.setColumnStretch(0, 0)
            grid.setColumnStretch(1, 1)
            grid.setColumnMinimumWidth(0, 140)
            layout.addLayout(grid)
            return group, grid
            
        def add_field(grid, row, label_text, widget):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #475569; border: none;")
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(100)
            lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            grid.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(widget, row, 1)
            widget.setStyleSheet("""
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #0F172A;
                    font-size: 13px;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 1px solid #38BDF8;
                    background-color: #FFFFFF;
                }
            """)

        # Personal Information
        g_personal, grid_personal = create_group("Personal Information")
        self.edit_display_name = QLineEdit()
        self.edit_display_name.setPlaceholderText("e.g. John Doe")
        add_field(grid_personal, 0, "Display Name:", self.edit_display_name)
        
        self.edit_university = QLineEdit()
        self.edit_university.setPlaceholderText("e.g. Vietnam-Korea University")
        add_field(grid_personal, 1, "University:", self.edit_university)
        
        self.combo_student_year = QComboBox()
        self.combo_student_year.addItem("1st Year", 1)
        self.combo_student_year.addItem("2nd Year", 2)
        self.combo_student_year.addItem("3rd Year", 3)
        self.combo_student_year.addItem("4th Year", 4)
        add_field(grid_personal, 2, "Student Year:", self.combo_student_year)
        
        self.edit_major = QLineEdit()
        self.edit_major.setPlaceholderText("e.g. Computer Science")
        add_field(grid_personal, 3, "Major / Field:", self.edit_major)

        self.edit_age = QLineEdit()
        self.edit_age.setPlaceholderText("e.g. 20")
        add_field(grid_personal, 4, "Age:", self.edit_age)

        self.edit_birth_year = QLineEdit()
        self.edit_birth_year.setPlaceholderText("e.g. 2006")
        add_field(grid_personal, 5, "Birth Year:", self.edit_birth_year)

        self.edit_phone = QLineEdit()
        self.edit_phone.setPlaceholderText("e.g. 0912345678")
        add_field(grid_personal, 6, "Phone Number:", self.edit_phone)
        
        fc_layout.addWidget(g_personal)

        # Academic Background
        g_academic, grid_academic = create_group("Academic Background")
        self.edit_gpa = QLineEdit()
        self.edit_gpa.setPlaceholderText("e.g. 3.8")
        add_field(grid_academic, 0, "Current GPA:", self.edit_gpa)
        
        self.edit_courses = QTextEdit()
        self.edit_courses.setPlaceholderText("e.g. Data Structures, Intro to AI")
        self.edit_courses.setFixedHeight(60)
        add_field(grid_academic, 1, "Current Courses:", self.edit_courses)
        
        self.edit_skills = QTextEdit()
        self.edit_skills.setPlaceholderText("e.g. Python, PyQt6, Machine Learning")
        self.edit_skills.setFixedHeight(60)
        add_field(grid_academic, 2, "Professional Skills:", self.edit_skills)
        fc_layout.addWidget(g_academic)

        # Career Goals
        g_career, grid_career = create_group("Career Goals")
        self.edit_interests = QTextEdit()
        self.edit_interests.setPlaceholderText("e.g. Web Development, Robotics")
        self.edit_interests.setFixedHeight(60)
        add_field(grid_career, 0, "Interests & Goals:", self.edit_interests)
        fc_layout.addWidget(g_career)

        # Class Schedule
        g_schedule, grid_schedule = create_group("Class Schedule")
        self.timetable_editor = TimetableEditor()
        add_field(grid_schedule, 0, "Manual Timetable:", self.timetable_editor)
        fc_layout.addWidget(g_schedule)
        
        # Save & Sync Button
        self.btn_save_sync = QPushButton("Save Profile")
        self.btn_save_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_sync.setMinimumHeight(45)
        self.btn_save_sync.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_save_sync.setStyleSheet("""
            QPushButton {
                background: #0F172A;
                color: white;
                border-radius: 12px;
                font-weight: 700;
                font-size: 14px;
                padding: 0 24px;
            }
            QPushButton:hover {
                background: #1E293B;
            }
        """)
        self.btn_save_sync.clicked.connect(self._handle_save_sync)
        fc_layout.addWidget(self.btn_save_sync)
        
        form_layout.addWidget(self.form_card)
        form_layout.addStretch()
        
        form_scroll.setFrameShape(QFrame.Shape.NoFrame)
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(form_widget)
        
        _THIN_SB = """
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;          /* Độ rộng thanh cuộn */
                margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #CBD5E1; 
            border-radius: 3px;  /* Bo tròn một nửa width */
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { 
            background: #94A3B8; 
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
            height: 0px; 
            border: none; 
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { 
            background: transparent; 
        }
        """
        form_scroll.verticalScrollBar().setStyleSheet(_THIN_SB)

        # 4. Tắt thanh cuộn ngang và tối ưu hóa trải nghiệm cuộn
        form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Nên bật thuộc tính này để cuộn mượt hơn bằng chuột/touchpad trên Windows
        form_scroll.verticalScrollBar().setSingleStep(15) 

        layout.addWidget(form_scroll)

    def init_portfolio_tab(self):
        layout = QVBoxLayout(self.portfolio_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.workspace_scroll = QScrollArea()
        self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.workspace_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        self.workspace_widget = QWidget()
        self.workspace_widget.setStyleSheet("background: transparent;")
        self.workspace_layout = QVBoxLayout(self.workspace_widget)
        self.workspace_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_layout.setSpacing(24)
        
        self.workspace_scroll.setWidget(self.workspace_widget)
        # Fix kỹ: set style trực tiếp lên scrollbar widget (Windows-safe)
        _THIN_SB = """
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1; border-radius: 2px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; border: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """
        self.workspace_scroll.verticalScrollBar().setStyleSheet(_THIN_SB)
        self.workspace_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.workspace_scroll)

    def init_hero_section(self):
        hero = ShadowCard(radius=28)
        hero.layout.setContentsMargins(0, 0, 0, 0)
        hero.layout.setSpacing(0)
        
        banner = QFrame()
        banner.setFixedHeight(120)
        banner.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #38BDF8);
            border-top-left-radius: 28px;
            border-top-right-radius: 28px;
        """)
        hero.layout.addWidget(banner)
        
        student = crud.get_current_student()
        display_name = student.get("display_name", "Student Name") if student else "Guest User"
        major = student.get("major", "AI Engineering Student") if student else "Undecided"
        
        ai_plan = None
        if student:
            ai_plan = student.get("context", {}).get("ai_plan")
            
        if ai_plan and isinstance(ai_plan, dict):
            bio = ai_plan.get("student_summary", "Passionate about creating elegant solutions through code.")
        else:
            bio = "Save your profile context and click Generate Plan to build your dynamic AI Academic Plan."
            
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(32, 0, 32, 32)
        
        top_row = QHBoxLayout()
        top_row.setSpacing(24)
        
        avatar = QLabel()
        avatar.setFixedSize(120, 120)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parts = display_name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[-1][0].upper()
        elif len(parts) == 1 and parts[0]:
            initials = parts[0][:2].upper()
        else:
            initials = "ST"
            
        avatar.setText(initials)
        avatar.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38BDF8, stop:1 #0284C7);
            color: white;
            border: 6px solid white;
            border-radius: 60px;
            font-weight: bold;
            font-size: 28px;
            margin-top: -60px;
        """)
        avatar_shadow = QGraphicsDropShadowEffect()
        avatar_shadow.setBlurRadius(30)
        avatar_shadow.setColor(QColor(18, 55, 105, 20))
        avatar_shadow.setOffset(0, 4)
        avatar.setGraphicsEffect(avatar_shadow)
        top_row.addWidget(avatar)
        
        info_v = QVBoxLayout()
        info_v.addSpacing(10)
        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet("color: #0F172A; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;")
        
        title_lbl = QLabel(major)
        title_lbl.setStyleSheet("color: #38BDF8; font-size: 16px; font-weight: 700;")
        
        info_v.addWidget(name_lbl)
        info_v.addWidget(title_lbl)
        top_row.addLayout(info_v)
        
        top_row.addStretch()
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(32)
        
        proj_count = "0"
        readiness = "0%"
        status_text = "EMPTY"
        
        if student:
            raw_input = student.get("context", {}).get("raw_input", {})
            proj_count = str(len(raw_input.get("academic_context", {}).get("current_courses", [])))
            status_text = student.get("context", {}).get("ai_status", "EMPTY")
            if ai_plan and isinstance(ai_plan, dict):
                readiness = f"{ai_plan.get('metrics', {}).get('career_readiness', 0)}%"
                
        for val, label in [(proj_count, "Courses"), (status_text, "AI Status"), (readiness, "Ready")]:
            stat_v = QVBoxLayout()
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet("color: #0F172A; font-size: 22px; font-weight: 800;")
            v_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 600; text-transform: uppercase;")
            l_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_v.addWidget(v_lbl)
            stat_v.addWidget(l_lbl)
            stats_layout.addLayout(stat_v)
            
        top_row.addLayout(stats_layout)
        c_layout.addLayout(top_row)
        
        bio_lbl = QLabel(bio)
        bio_lbl.setWordWrap(True)
        bio_lbl.setStyleSheet("color: #475569; font-size: 15px; margin-top: 16px; line-height: 1.6;")
        c_layout.addWidget(bio_lbl)
        
        hero.layout.addWidget(content)
        self.workspace_layout.addWidget(hero)

    def init_skills_achievements(self):
        layout = QHBoxLayout()
        layout.setSpacing(24)
        
        skills_card = ShadowCard()
        skills_card.layout.setSpacing(20)
        
        h_layout = QHBoxLayout()
        st_lbl = QLabel("Academic & Professional Skills")
        st_lbl.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        h_layout.addWidget(st_lbl)
        h_layout.addStretch()
        skills_card.layout.addLayout(h_layout)
        
        skills_flow = QGridLayout()
        skills_flow.setSpacing(10)
        
        student = crud.get_current_student()
        skills_list = []
        if student:
            ai_plan = student.get("context", {}).get("ai_plan")
            if ai_plan and isinstance(ai_plan, dict):
                strengths = ai_plan.get("skill_analysis", {}).get("strengths", [])
                skills_list = [(s, "AI Verified") for s in strengths]
                
            if not skills_list:
                raw_skills = student.get("context", {}).get("raw_input", {}).get("student_info", {}).get("skills", [])
                skills_list = [(s, "Custom") for s in raw_skills]
                
        if not skills_list:
            skills_list = [("Python", "Skill"), ("PyQt6", "Skill"), ("Git", "Skill")]
            
        for i, (name, lvl) in enumerate(skills_list[:8]):
            row, col = divmod(i, 2)
            skills_flow.addWidget(SkillChip(name, lvl), row, col)
            
        skills_card.layout.addLayout(skills_flow)
        layout.addWidget(skills_card, 1)
        
        ach_card = ShadowCard()
        ach_card.layout.setSpacing(20)
        ach_lbl = QLabel("Recommendations / Focus")
        ach_lbl.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        ach_card.layout.addWidget(ach_lbl)
        
        focus_items = []
        if student:
            ai_plan = student.get("context", {}).get("ai_plan")
            if ai_plan and isinstance(ai_plan, dict):
                focus_areas = ai_plan.get("skill_analysis", {}).get("recommended_focus", [])
                for f in focus_areas:
                    focus_items.append(("🎯", "Recommended Focus", f))
                    
        if not focus_items:
            focus_items = [
                ("🏆", "Default Goal", "Generate study plan to calculate recommendations"),
                ("📜", "Skill Target", "Add your courses to begin verification")
            ]
            
        for icon, title, sub in focus_items[:3]:
            row = QHBoxLayout()
            row.setSpacing(12)
            ic_lbl = QLabel(icon)
            ic_lbl.setFixedSize(40, 40)
            ic_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic_lbl.setStyleSheet("background: #F0F9FF; border-radius: 12px; font-size: 20px;")
            
            t_v = QVBoxLayout()
            t_l = QLabel(title)
            t_l.setStyleSheet("color: #0F172A; font-weight: 700; font-size: 14px;")
            s_l = QLabel(sub)
            s_l.setStyleSheet("color: #64748B; font-size: 12px;")
            t_v.addWidget(t_l); t_v.addWidget(s_l)
            
            row.addWidget(ic_lbl)
            row.addLayout(t_v)
            row.addStretch()
            ach_card.layout.addLayout(row)
            
        layout.addWidget(ach_card, 1)
        self.workspace_layout.addLayout(layout)

    def init_portfolio(self):
        section_lbl = QLabel("Featured Study Tracks & Courses")
        section_lbl.setStyleSheet("color: #0F172A; font-size: 22px; font-weight: 800; margin-top: 12px;")
        self.workspace_layout.addWidget(section_lbl)
        
        grid = QGridLayout()
        grid.setSpacing(24)
        
        student = crud.get_current_student()
        courses_list = []
        if student:
            raw_input = student.get("context", {}).get("raw_input", {})
            courses_list = raw_input.get("academic_context", {}).get("current_courses", [])
            
        if not courses_list:
            courses_list = ["No Courses Added Yet"]
            
        for i, course_name in enumerate(courses_list[:3]):
            grid.addWidget(ProjectCard(course_name, ["Course", "Academic"], "Part of your active student profile study plan."), 0, i)
            
        self.workspace_layout.addLayout(grid)

    def init_timelines(self):
        layout = QHBoxLayout()
        layout.setSpacing(24)
        
        student = crud.get_current_student()
        roadmap = []
        if student:
            ai_plan = student.get("context", {}).get("ai_plan")
            if ai_plan and isinstance(ai_plan, dict):
                roadmap = ai_plan.get("academic_roadmap", [])
                
        aca_card = ShadowCard()
        aca_card.layout.addWidget(QLabel("AI Academic Roadmap", styleSheet="color: #0F172A; font-size: 18px; font-weight: 700;"))
        
        if roadmap:
            for i, item in enumerate(roadmap[:3]):
                title = item.get("title", "Course Plan")
                status = item.get("status", "planned").replace("_", " ").title()
                insight = item.get("ai_insight", "")
                progress = item.get("progress_pct", 0)
                is_last = (i == len(roadmap[:3]) - 1)
                
                subtitle = f"Status: {status} ({progress}%)"
                if insight:
                    subtitle += f"\nAI Insight: {insight}"
                aca_card.layout.addWidget(TimelineItem(title, subtitle, "Roadmap", is_last=is_last))
        else:
            aca_card.layout.addWidget(TimelineItem("B.Sc in AI & Data Science", "VKU University", "2021 - Present"))
            aca_card.layout.addWidget(TimelineItem("No AI Roadmap Available", "Please trigger plan generation on the Dashboard.", "Planned", is_last=True))
            
        layout.addWidget(aca_card, 1)
        
        car_card = ShadowCard()
        car_card.layout.addWidget(QLabel("Career Journey Plan", styleSheet="color: #0F172A; font-size: 18px; font-weight: 700;"))
        
        target_role = "Software Engineer"
        interests = []
        if student:
            raw_input = student.get("context", {}).get("raw_input", {})
            interests = raw_input.get("career_goals", {}).get("interests", [])
            
        car_card.layout.addWidget(TimelineItem(f"Target: {target_role}", ", ".join(interests) if interests else "AI Developer / Web Architect", "Goal"))
        car_card.layout.addWidget(TimelineItem("Active Learner Profile", "Tracking local sync and academic plan progress", "Current", is_last=True))
        layout.addWidget(car_card, 1)
        
        self.workspace_layout.addLayout(layout)

    def init_activity(self):
        act_card = ShadowCard()
        h_box = QHBoxLayout()
        h_box.addWidget(QLabel("Local Sync Activity Log", styleSheet="color: #0F172A; font-size: 18px; font-weight: 700;"))
        h_box.addStretch()
        act_card.layout.addLayout(h_box)
        
        student = crud.get_current_student()
        is_dirty = 0
        status_text = "EMPTY"
        updated_at = "Unknown"
        if student:
            is_dirty = student.get("context", {}).get("is_dirty", 0) or student.get("is_dirty", 0)
            status_text = student.get("context", {}).get("ai_status", "EMPTY")
            updated_at = student.get("context", {}).get("updated_at", "")[:19].replace("T", " ")
            
        sync_status = "Pending Sync" if is_dirty else "Synchronized with Backend"
        
        for text, time in [
            (f"AI Plan Status: {status_text}", updated_at),
            (f"Local SQLite Sync Status: {sync_status}", "Realtime")
        ]:
            row = QHBoxLayout()
            row.setContentsMargins(0, 8, 0, 8)
            t_lbl = QLabel(text)
            t_lbl.setStyleSheet("color: #475569; font-size: 14px;")
            time_lbl = QLabel(time)
            time_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            row.addWidget(t_lbl)
            row.addStretch()
            row.addWidget(time_lbl)
            act_card.layout.addLayout(row)
            
        self.workspace_layout.addWidget(act_card)

    def _setup_insights_panel(self):
        self.insights_container = QWidget()
        self.insights_content_layout = QVBoxLayout(self.insights_container)
        self.insights_content_layout.setContentsMargins(0, 0, 0, 0)
        self.insights_content_layout.setSpacing(24)
        
        self._populate_insights(self.insights_content_layout)
        return self.insights_container

    def _populate_insights(self, layout):
        student = crud.get_current_student()
        recommendation_text = "Your plan is ready. Update your profile info to recalculate insights."
        
        ai_plan = None
        if student:
            ai_plan = student.get("context", {}).get("ai_plan")
            
        if ai_plan and isinstance(ai_plan, dict):
            focus_areas = ai_plan.get("skill_analysis", {}).get("recommended_focus", [])
            if focus_areas:
                recommendation_text = "Recommended Skills to target:\n" + "\n".join([f"• {f}" for f in focus_areas])
            else:
                recommendation_text = "Academic profile successfully generated! View your study roadmap below."
        elif student:
            recommendation_text = "Profile saved locally. Please trigger AI Academic Plan generation to calculate recommendations."
            
        ai_card = ShadowCard()
        ai_card.setStyleSheet(ai_card.styleSheet() + " #ShadowCard { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0F172A, stop:1 #1E293B); border: none; }")
        ai_card.layout.setSpacing(12)
        
        ai_title = QLabel("AI Recommendations")
        ai_title.setStyleSheet("color: #38BDF8; font-size: 14px; font-weight: 800; text-transform: uppercase; background: transparent; border: none;")
        ai_card.layout.addWidget(ai_title)
        
        tip = QLabel(recommendation_text)
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #E2E8F0; font-size: 13px; line-height: 1.5; background: transparent; border: none;")
        ai_card.layout.addWidget(tip)
        
        opt_btn = QPushButton("Generate/Refresh Plan")
        opt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        opt_btn.setStyleSheet("background: #38BDF8; color: #0F172A; border-radius: 8px; height: 36px; font-weight: 700; font-size: 12px;")
        opt_btn.clicked.connect(self._trigger_ai_plan_from_portfolio)
        ai_card.layout.addWidget(opt_btn)
        
        layout.addWidget(ai_card)
        
        goals_card = ShadowCard()
        goals_card.layout.addWidget(QLabel("Upcoming Goals", styleSheet="color: #0F172A; font-size: 16px; font-weight: 700;"))
        
        goals = []
        if ai_plan and isinstance(ai_plan, dict):
            roadmap = ai_plan.get("academic_roadmap", [])
            for item in roadmap:
                if item.get("status") == "in_progress":
                    goals.append((item.get("title", ""), "Target"))
            
        if not goals:
            goals = [("AWS Certification", "Oct 24"), ("Academic Plan V2", "Nov 12")]
            
        for goal, date in goals:
            g_row = QHBoxLayout()
            g_lbl = QLabel(goal)
            g_lbl.setWordWrap(True)
            g_lbl.setStyleSheet("color: #475569; font-size: 13px; font-weight: 600;")
            d_lbl = QLabel(date)
            d_lbl.setWordWrap(False)
            d_lbl.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700; background: #F0F9FF; padding: 2px 6px; border-radius: 4px;")
            g_row.addWidget(g_lbl); g_row.addStretch(); g_row.addWidget(d_lbl)
            goals_card.layout.addLayout(g_row)
            
        layout.addWidget(goals_card)
        
        # GPA / Readiness stats
        gpa_val = "0.0"
        readiness_val = "0%"
        if student:
            gpa_raw = student.get("context", {}).get("raw_input", {}).get("student_info", {}).get("gpa", 0.0)
            try:
                gpa_val = f"{float(gpa_raw):.2f}"
            except:
                gpa_val = "0.0"
            if ai_plan and isinstance(ai_plan, dict):
                readiness_val = f"{ai_plan.get('metrics', {}).get('career_readiness', 0)}%"
                
        ana_card = ShadowCard()
        ana_card.layout.addWidget(QLabel("Profile Analytics", styleSheet="color: #0F172A; font-size: 16px; font-weight: 700;"))
        
        ana_row = QHBoxLayout()
        for v, l in [(gpa_val, "GPA"), (readiness_val, "Career Ready")]:
            v_v = QVBoxLayout()
            v_l = QLabel(v); v_l.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 800;"); v_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l_l = QLabel(l); l_l.setStyleSheet("color: #64748B; font-size: 11px;"); l_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v_v.addWidget(v_l); v_v.addWidget(l_l)
            ana_row.addLayout(v_v)
        ana_card.layout.addLayout(ana_row)
        
        layout.addWidget(ana_card)
        layout.addStretch()

    def _trigger_ai_plan_from_portfolio(self):
        if self.controller and hasattr(self.controller, "show_page"):
            self.controller.show_page(0)
            dashboard_page = self.controller.pages_container.widget(0)
            if dashboard_page and hasattr(dashboard_page, "start_generation"):
                dashboard_page.start_generation()

    def _handle_save_sync(self):
        student = crud.get_current_student()
        if not student:
            QMessageBox.warning(self, "Error", "No logged-in student session found.")
            return
            
        student_id = student["id"]
        email = student["email"]
        username = student["username"]
        
        display_name = self.edit_display_name.text().strip()
        university = self.edit_university.text().strip()
        major = self.edit_major.text().strip()
        student_year = self.combo_student_year.currentData() or 1
        
        age_str = self.edit_age.text().strip()
        birth_year_str = self.edit_birth_year.text().strip()
        phone = self.edit_phone.text().strip()
        
        age = int(age_str) if age_str.isdigit() else None
        birth_year = int(birth_year_str) if birth_year_str.isdigit() else None

        # Validate GPA
        try:
            gpa = float(self.edit_gpa.text().strip() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Invalid GPA", "GPA must be a valid number (e.g. 3.8).")
            return
            
        def parse_list(txt_edit):
            text = txt_edit.toPlainText().strip()
            if not text:
                return []
            return [x.strip() for x in text.split(",") if x.strip()]
            
        courses = parse_list(self.edit_courses)
        skills = parse_list(self.edit_skills)
        interests = parse_list(self.edit_interests)
        
        raw_input = {
            "student_info": {
                "full_name": display_name,
                "major": major,
                "current_semester": student_year * 2 - 1,
                "gpa": gpa,
                "skills": skills,
                "university": university,
                "age": age_str,
                "birth_year": birth_year_str,
                "phone": phone
            },
            "academic_context": {
                "current_courses": courses,
                "completed_courses": [],
                "timetable_manual": self.timetable_editor.get_data()
            },
            "career_goals": {
                "target_role": "",
                "interests": interests
            }
        }
        
        # Save to SQLite local database with is_dirty=1 (both profile and context)
        crud.save_student_profile(
            student_id=student_id,
            email=email,
            username=username,
            display_name=display_name,
            major=major,
            student_year=student_year,
            university=university,
            birth_year=birth_year,
            age=age,
            phone=phone,
            is_dirty=1
        )
        
        context_data = student.get("context", {})
        ai_plan = context_data.get("ai_plan")
        ai_status = context_data.get("ai_status", "EMPTY")
        ai_last_error = context_data.get("ai_last_error")
        
        crud.save_student_context(
            student_id=student_id,
            raw_input_dict=raw_input,
            ai_plan_dict=ai_plan,
            ai_status=ai_status,
            ai_last_error=ai_last_error,
            is_dirty=1
        )
        
        # Update user info in sidebar
        main_win = self.window()
        if main_win and hasattr(main_win, "sidebar"):
            main_win.sidebar.update_user_info(display_name, major)
            
        QMessageBox.information(self, "Profile Saved", "Your academic profile changes have been saved locally. They will sync to the server automatically during plan generation.")
        
        # Switch to dashboard page and start AI generation
        if self.controller and hasattr(self.controller, "show_page"):
            self.controller.show_page(0)
            dashboard_page = self.controller.pages_container.widget(0)
            if dashboard_page and hasattr(dashboard_page, "start_generation"):
                dashboard_page.start_generation()

    def load_data(self):
        student = crud.get_current_student()
        if not student:
            return
            
        display_name = student.get("display_name", "") or ""
        major = student.get("major", "") or ""
        student_year = student.get("student_year", 1) or 1
        university = student.get("university", "") or ""
        age = student.get("age", "") or ""
        birth_year = student.get("birth_year", "") or ""
        phone = student.get("phone", "") or ""
        
        self.edit_display_name.setText(display_name)
        self.edit_university.setText(university)
        self.edit_major.setText(major)
        self.edit_age.setText(str(age) if age is not None and age != "" else "")
        self.edit_birth_year.setText(str(birth_year) if birth_year is not None and birth_year != "" else "")
        self.edit_phone.setText(phone)
        
        idx = self.combo_student_year.findData(student_year)
        if idx >= 0:
            self.combo_student_year.setCurrentIndex(idx)
            
        context_data = student.get("context", {})
        raw_input = context_data.get("raw_input", {})
        
        student_info = raw_input.get("student_info", {})
        gpa = student_info.get("gpa", 0.0)
        skills = student_info.get("skills", [])
        
        academic_context = raw_input.get("academic_context", {})
        courses = academic_context.get("current_courses", [])
        
        career_goals = raw_input.get("career_goals", {})
        interests = career_goals.get("interests", [])
        
        self.edit_gpa.setText(str(gpa))
        self.edit_courses.setText(", ".join(courses))
        self.edit_skills.setText(", ".join(skills))
        self.edit_interests.setText(", ".join(interests))
        
        self.timetable_editor.clear()
        timetable_manual = academic_context.get("timetable_manual", [])
        for row_data in timetable_manual:
            self.timetable_editor.add_row(row_data)
        
        # Update mini avatar initials
        parts = display_name.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[-1][0].upper()
        elif len(parts) == 1 and parts[0]:
            initials = parts[0][:2].upper()
        else:
            initials = "ST"
        self.mini_avatar.setText(initials)

    def refresh(self):
        self.load_data()
        self.refresh_gpa_manager()
        
        # Rebuild the portfolio tab
        self._clear_layout(self.workspace_layout)
        
        self.init_hero_section()
        self.init_skills_achievements()
        self.init_portfolio()
        self.init_timelines()
        self.init_activity()
        
        # Rebuild the insights panel
        if hasattr(self, "insights_content_layout"):
            self._clear_layout(self.insights_content_layout)
            self._populate_insights(self.insights_content_layout)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def init_gpa_tab(self):
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDoubleSpinBox
        gpa_layout = QVBoxLayout(self.gpa_tab)
        gpa_layout.setContentsMargins(16, 16, 16, 16)
        gpa_layout.setSpacing(16)

        # ── TOP STATS BAR ──────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(16)

        # GPA Circular Indicator card
        left_stats = ShadowCard(radius=16)
        left_stats.setFixedWidth(200)
        left_stats.layout.setSpacing(10)
        left_stats.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        gpa_lbl_header = QLabel("Điểm Tích Lũy (Thang 4)")
        gpa_lbl_header.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 800; border: none; background: transparent;")
        gpa_lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_stats.layout.addWidget(gpa_lbl_header)

        self.gpa_circle_widget = QWidget()
        self.gpa_circle_widget.setFixedSize(120, 120)
        self.gpa_circle_widget.paintEvent = self._draw_gpa_circle
        left_stats.layout.addWidget(self.gpa_circle_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.gpa_val_display = QLabel("0.00")
        self.gpa_val_display.setStyleSheet("font-size: 26px; font-weight: 900; color: #0F172A; border: none; background: transparent;")
        self.gpa_val_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_stats.layout.addWidget(self.gpa_val_display)

        self.gpa_credits_lbl = QLabel("Tổng tín chỉ: 0")
        self.gpa_credits_lbl.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        self.gpa_credits_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_stats.layout.addWidget(self.gpa_credits_lbl)

        top_bar.addWidget(left_stats)

        # Summary stat cards
        self.stat_t10_lbl = QLabel("0.00")
        self.stat_xeploai_lbl = QLabel("--")
        self.stat_credits_reg_lbl = QLabel("0")

        def _make_stat_card(title, value_lbl, color="#0F172A"):
            card = ShadowCard(radius=14)
            card.layout.setSpacing(6)
            card.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            t = QLabel(title)
            t.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700; border: none; background: transparent;")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.layout.addWidget(t)
            value_lbl.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {color}; border: none; background: transparent;")
            value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.layout.addWidget(value_lbl)
            return card

        top_bar.addWidget(_make_stat_card("Điểm Tích Lũy (Thang 10)", self.stat_t10_lbl, "#2563EB"), 1)
        top_bar.addWidget(_make_stat_card("Xếp Loại Tích Lũy", self.stat_xeploai_lbl, "#059669"), 1)
        top_bar.addWidget(_make_stat_card("TC Tích Lũy", self.stat_credits_reg_lbl, "#7C3AED"), 1)

        # Add Semester button card
        btn_card = ShadowCard(radius=14)
        btn_card.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_add_semester = QPushButton("+ Thêm Học Kỳ")
        self.btn_add_semester.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_semester.setStyleSheet("""
            QPushButton {
                background: #2563EB; color: white; border-radius: 8px; font-weight: bold;
                padding: 10px 18px; font-size: 13px; border: none;
            }
            QPushButton:hover { background: #1D4ED8; }
        """)
        self.btn_add_semester.clicked.connect(self._add_semester_dialog)
        btn_card.layout.addWidget(self.btn_add_semester)
        top_bar.addWidget(btn_card)

        gpa_layout.addLayout(top_bar)

        # ── MAIN SCROLL AREA ───────────────────────────────────────────────────
        self.semesters_scroll = QScrollArea()
        self.semesters_scroll.setWidgetResizable(True)
        self.semesters_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.semesters_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.semesters_content = QWidget()
        self.semesters_content.setStyleSheet("background: transparent;")
        self.semesters_layout = QVBoxLayout(self.semesters_content)
        self.semesters_layout.setContentsMargins(0, 0, 4, 0)
        self.semesters_layout.setSpacing(20)
        self.semesters_layout.addStretch()

        self.semesters_scroll.setWidget(self.semesters_content)
        # Fix kỹ: set style trực tiếp lên scrollbar widget (Windows-safe)
        _THIN_SB = """
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1; border-radius: 2px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; border: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """
        self.semesters_scroll.verticalScrollBar().setStyleSheet(_THIN_SB)
        self.semesters_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        gpa_layout.addWidget(self.semesters_scroll, 1)

    def _draw_gpa_circle(self, event):
        painter = QPainter(self.gpa_circle_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            gpa = float(self.gpa_val_display.text())
        except ValueError:
            gpa = 0.0

        w = self.gpa_circle_widget.width()
        h = self.gpa_circle_widget.height()
        margin = 10
        arc_rect_size = min(w, h) - margin * 2

        # Draw background track
        pen_bg = QPen(QColor("#E2E8F0"))
        pen_bg.setWidth(10)
        painter.setPen(pen_bg)
        painter.drawArc(margin, margin, arc_rect_size, arc_rect_size, -30 * 16, 240 * 16)

        # Draw progress arc
        pen_fg = QPen()
        pen_fg.setWidth(10)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)

        grad = QLinearGradient(margin, margin, margin + arc_rect_size, margin + arc_rect_size)
        if gpa >= 3.6:
            grad.setColorAt(0, QColor("#10B981"))
            grad.setColorAt(1, QColor("#3B82F6"))
        elif gpa >= 3.0:
            grad.setColorAt(0, QColor("#3B82F6"))
            grad.setColorAt(1, QColor("#8B5CF6"))
        elif gpa >= 2.0:
            grad.setColorAt(0, QColor("#F59E0B"))
            grad.setColorAt(1, QColor("#EF4444"))
        else:
            grad.setColorAt(0, QColor("#EF4444"))
            grad.setColorAt(1, QColor("#F43F5E"))

        pen_fg.setBrush(QBrush(grad))
        painter.setPen(pen_fg)

        progress_angle = int((gpa / 4.0) * 240)
        painter.drawArc(margin, margin, arc_rect_size, arc_rect_size, -210 * 16, -progress_angle * 16)
        painter.end()

    def refresh_gpa_manager(self):
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDoubleSpinBox
        student = crud.get_current_student()
        if not student:
            return

        student_id = student["id"]
        grades = crud.get_student_grades(student_id)

        # Calculate GPA
        cum_gpa, sem_gpas = crud.calculate_gpa(student_id)

        # Update stat cards
        self.gpa_val_display.setText(f"{cum_gpa:.2f}")
        cum_t10 = round(cum_gpa * 10 / 4, 2) if cum_gpa > 0 else 0.0
        self.stat_t10_lbl.setText(f"{cum_t10:.2f}")

        if cum_gpa >= 3.6:
            xep_loai = "Xuất Sắc"
            xep_color = "#059669"
        elif cum_gpa >= 3.2:
            xep_loai = "Giỏi"
            xep_color = "#2563EB"
        elif cum_gpa >= 2.5:
            xep_loai = "Khá"
            xep_color = "#D97706"
        elif cum_gpa >= 2.0:
            xep_loai = "Trung Bình"
            xep_color = "#64748B"
        else:
            xep_loai = "Yếu"
            xep_color = "#EF4444"
        self.stat_xeploai_lbl.setText(xep_loai)
        self.stat_xeploai_lbl.setStyleSheet(f"font-size: 20px; font-weight: 900; color: {xep_color}; border: none; background: transparent;")

        valid_all = [g for g in grades if not (g["course_name"] == "Semester Started" and g["credits"] == 0)]
        total_credits = sum(g["credits"] for g in valid_all)
        self.gpa_credits_lbl.setText(f"Tổng tín chỉ: {total_credits}")
        self.stat_credits_reg_lbl.setText(str(total_credits))
        self.edit_gpa.setText(f"{cum_gpa:.2f}")
        self.gpa_circle_widget.update()

        # ── Clear semesters layout ─────────────────────────────────────────────
        for i in reversed(range(self.semesters_layout.count())):
            item = self.semesters_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
            elif item:
                self.semesters_layout.removeItem(item)

        grades_by_sem = {}
        for g in grades:
            sem = g["semester"]
            if sem not in grades_by_sem:
                grades_by_sem[sem] = []
            grades_by_sem[sem].append(g)

        if not grades_by_sem:
            grades_by_sem = {"Học kỳ 1": []}

        # ── Semester Summary Table ─────────────────────────────────────────────
        TABLE_STYLE = """
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                gridline-color: transparent;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #374151;
                color: #FFFFFF;
                font-weight: 700;
                padding: 8px 6px;
                border: none;
                border-right: 1px solid #4B5563;
                font-size: 12px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E5E7EB;
                padding: 7px 6px;
                color: #111827;
            }
            QTableWidget::item:alternate {
                background-color: #F9FAFB;
            }
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1; border-radius: 2px; min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #94A3B8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; border: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
            QScrollBar:horizontal {
                border: none; background: transparent;
                height: 4px; margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #CBD5E1; border-radius: 2px; min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover { background: #94A3B8; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; border: none; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
        """

        summary_frame = QFrame()
        summary_frame.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }")
        sum_lay = QVBoxLayout(summary_frame)
        sum_lay.setContentsMargins(0, 0, 0, 0)
        sum_lay.setSpacing(0)

        summary_table = QTableWidget()
        SUM_COLS = ["#", "Học kỳ", "Số TC-ĐK", "Điểm 4", "Điểm 10", "TC TL HK", "Xếp loại", "Điểm 4 TL", "Điểm 10 TL", "TC Tích lũy"]
        summary_table.setColumnCount(len(SUM_COLS))
        summary_table.setHorizontalHeaderLabels(SUM_COLS)
        summary_table.setFrameShape(QFrame.Shape.NoFrame)
        summary_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        summary_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        summary_table.setShowGrid(False)
        summary_table.setAlternatingRowColors(True)
        summary_table.verticalHeader().setVisible(False)
        sh = summary_table.horizontalHeader()
        sh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for c in [0, 2, 3, 4, 5, 6, 7, 8, 9]:
            sh.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        summary_table.setStyleSheet(TABLE_STYLE)

        sem_list = sorted(grades_by_sem.keys())
        summary_table.setRowCount(len(sem_list))

        cum_credits_acc = 0
        cum_weighted_acc = 0.0

        for row_idx, sem_name in enumerate(sem_list):
            sem_grades = grades_by_sem[sem_name]
            valid_grades = [g for g in sem_grades if not (g["course_name"] == "Semester Started" and g["credits"] == 0)]

            tc_dk = sum(g["credits"] for g in valid_grades)
            sem_gpa4 = sem_gpas.get(sem_name, 0.0)
            sem_t10 = round(sem_gpa4 * 10 / 4, 2) if sem_gpa4 > 0 else 0.0

            cum_credits_acc += tc_dk
            cum_weighted_acc += sem_gpa4 * tc_dk
            cum_gpa4_acc = round(cum_weighted_acc / cum_credits_acc, 2) if cum_credits_acc > 0 else 0.0
            cum_t10_acc = round(cum_gpa4_acc * 10 / 4, 2) if cum_gpa4_acc > 0 else 0.0

            if cum_gpa4_acc >= 3.6:
                xl = "Xuất Sắc"; xl_color = "#059669"
            elif cum_gpa4_acc >= 3.2:
                xl = "Giỏi"; xl_color = "#2563EB"
            elif cum_gpa4_acc >= 2.5:
                xl = "Khá"; xl_color = "#D97706"
            elif cum_gpa4_acc >= 2.0:
                xl = "Trung Bình"; xl_color = "#64748B"
            else:
                xl = "Yếu"; xl_color = "#EF4444"

            def _item(text, align=Qt.AlignmentFlag.AlignCenter, bold=False, color=None):
                it = QTableWidgetItem(str(text))
                it.setTextAlignment(align)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if bold:
                    font = it.font(); font.setBold(True); it.setFont(font)
                if color:
                    it.setForeground(QColor(color))
                return it

            summary_table.setItem(row_idx, 0, _item(row_idx + 1))
            summary_table.setItem(row_idx, 1, _item(sem_name, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
            summary_table.setItem(row_idx, 2, _item(tc_dk))
            summary_table.setItem(row_idx, 3, _item(f"{sem_gpa4:.2f}", color="#EF4444" if sem_gpa4 < 2.0 else None))
            summary_table.setItem(row_idx, 4, _item(f"{sem_t10:.2f}"))
            summary_table.setItem(row_idx, 5, _item(tc_dk))
            xl_item = _item(xl, color=xl_color, bold=True)
            summary_table.setItem(row_idx, 6, xl_item)
            summary_table.setItem(row_idx, 7, _item(f"{cum_gpa4_acc:.2f}", bold=True))
            summary_table.setItem(row_idx, 8, _item(f"{cum_t10_acc:.2f}", bold=True))
            summary_table.setItem(row_idx, 9, _item(cum_credits_acc, bold=True))

        n_sum_rows = max(1, len(sem_list))
        summary_table.setFixedHeight(n_sum_rows * 36 + 38)
        sum_lay.addWidget(summary_table)
        self.semesters_layout.addWidget(summary_frame)

        # ── Per-Semester Detail Tables ─────────────────────────────────────────
        DETAIL_COLS = ["#", "Tên lớp học phần", "Số TC", "Lần học",
                       "Điểm CC / GVHD", "Điểm Bài tập", "Điểm Giữa kỳ",
                       "Điểm Cuối kỳ / Đồ Án", "Điểm T10", "Điểm Chữ", ""]

        for sem_name in sem_list:
            sem_grades = grades_by_sem[sem_name]
            sem_gpa = sem_gpas.get(sem_name, 0.0)
            valid_grades = [g for g in sem_grades if not (g["course_name"] == "Semester Started" and g["credits"] == 0)]

            sem_frame = QFrame()
            sem_frame.setStyleSheet("QFrame { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }")
            sem_lay = QVBoxLayout(sem_frame)
            sem_lay.setContentsMargins(0, 0, 0, 12)
            sem_lay.setSpacing(0)

            # Header row
            hdr_widget = QWidget()
            hdr_widget.setStyleSheet("background: transparent;")
            hdr = QHBoxLayout(hdr_widget)
            hdr.setContentsMargins(12, 10, 12, 10)

            lbl_title = QLabel(f"Điểm các lớp học phần")
            lbl_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #2563EB; border: none; background: transparent;")
            hdr.addWidget(lbl_title)
            hdr.addStretch()

            sem_badge = QLabel(sem_name)
            sem_badge.setStyleSheet("font-size: 12px; font-weight: 700; color: #FFFFFF; background: #374151; padding: 3px 10px; border-radius: 6px; border: none;")
            hdr.addWidget(sem_badge)

            lbl_gpa = QLabel(f"GPA: {sem_gpa:.2f}")
            lbl_gpa.setStyleSheet("font-size: 12px; font-weight: bold; color: #2563EB; background: #EFF6FF; padding: 3px 10px; border-radius: 6px; border: none;")
            hdr.addWidget(lbl_gpa)

            btn_del_sem = QPushButton("Xóa HK")
            btn_del_sem.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del_sem.setFixedHeight(28)
            btn_del_sem.setStyleSheet("""
                QPushButton { background: transparent; color: #EF4444; border: 1px solid #FECACA;
                    border-radius: 5px; font-size: 11px; font-weight: bold; padding: 0 10px; }
                QPushButton:hover { background: #FEF2F2; }
            """)
            btn_del_sem.clicked.connect(lambda checked, s=sem_name: self._delete_semester(s))
            hdr.addWidget(btn_del_sem)
            sem_lay.addWidget(hdr_widget)

            # Separator line
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("background: #E5E7EB; max-height: 1px; border: none;")
            sem_lay.addWidget(sep)

            # Grade table
            table = QTableWidget()
            table.setColumnCount(len(DETAIL_COLS))
            table.setHorizontalHeaderLabels(DETAIL_COLS)
            table.setFrameShape(QFrame.Shape.NoFrame)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            table.setShowGrid(False)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)
            dh = table.horizontalHeader()
            dh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            for c in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                dh.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
            table.setStyleSheet(TABLE_STYLE)

            GRADE_LETTER_COLORS = {
                "A": "#059669", "B+": "#2563EB", "B": "#2563EB",
                "C+": "#D97706", "C": "#D97706",
                "D+": "#EF4444", "D": "#EF4444", "F": "#EF4444"
            }

            table.setRowCount(len(valid_grades))
            for idx, g in enumerate(valid_grades):
                def _di(text, align=Qt.AlignmentFlag.AlignCenter, color=None, bold=False):
                    it = QTableWidgetItem(str(text) if text is not None else "")
                    it.setTextAlignment(align)
                    it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if color: it.setForeground(QColor(color))
                    if bold:
                        f = it.font(); f.setBold(True); it.setFont(f)
                    return it

                table.setItem(idx, 0, _di(idx + 1))
                table.setItem(idx, 1, _di(g["course_name"], Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
                table.setItem(idx, 2, _di(g["credits"]))
                table.setItem(idx, 3, _di(g.get("attempt") or 1))
                table.setItem(idx, 4, _di(f"{g['grade_cc']:.1f}" if g.get("grade_cc") is not None else "", color="#2563EB" if g.get("grade_cc") is not None else None))
                table.setItem(idx, 5, _di(f"{g['grade_bt']:.1f}" if g.get("grade_bt") is not None else ""))
                table.setItem(idx, 6, _di(f"{g['grade_gk']:.1f}" if g.get("grade_gk") is not None else ""))
                table.setItem(idx, 7, _di(f"{g['grade_ck']:.1f}" if g.get("grade_ck") is not None else ""))
                t10_val = g.get("grade_t10")
                if t10_val is None:
                    t10_val = round(g["grade_value"] * 10 / 4, 1)
                table.setItem(idx, 8, _di(f"{t10_val:.1f}", bold=True))
                letter = g.get("grade_letter", "")
                table.setItem(idx, 9, _di(letter, color=GRADE_LETTER_COLORS.get(letter, "#0F172A"), bold=True))

                btn_del = QPushButton("✕")
                btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_del.setFixedSize(22, 22)
                btn_del.setStyleSheet("""
                    QPushButton { color: #9CA3AF; border: none; background: transparent; font-size: 12px; font-weight: bold; }
                    QPushButton:hover { color: #EF4444; background: #FEE2E2; border-radius: 4px; }
                """)
                btn_del.clicked.connect(lambda checked, gid=g["id"]: self._delete_course(gid))
                cw = QWidget(); cl = QHBoxLayout(cw)
                cl.setContentsMargins(0, 0, 0, 0)
                cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cl.addWidget(btn_del)
                table.setCellWidget(idx, 10, cw)

            row_h = 36
            table_h = len(valid_grades) * row_h + 38 if valid_grades else 38
            table.setFixedHeight(table_h)
            sem_lay.addWidget(table)

            if not valid_grades:
                lbl_empty = QLabel("  Chưa có môn học nào trong học kỳ này.")
                lbl_empty.setStyleSheet("color: #9CA3AF; font-size: 12px; font-style: italic; border: none; background: transparent; padding: 8px;")
                sem_lay.addWidget(lbl_empty)

            # ── Add Course Form ────────────────────────────────────────────────
            form_widget = QWidget()
            form_widget.setStyleSheet("background: #F8FAFC; border-top: 1px solid #E5E7EB; border-radius: 0 0 10px 10px;")
            form_outer = QVBoxLayout(form_widget)
            form_outer.setContentsMargins(12, 10, 12, 8)
            form_outer.setSpacing(6)

            def _lbl(t):
                l = QLabel(t)
                l.setStyleSheet("font-size: 11px; color: #6B7280; border: none; background: transparent;")
                return l

            # ── Row 1: Tên môn + TC + Điểm chữ ───────────────────────────────
            row1 = QHBoxLayout()
            row1.setSpacing(8)

            edit_course = QLineEdit()
            edit_course.setPlaceholderText("Tên môn học...")
            edit_course.setFixedHeight(30)
            edit_course.setStyleSheet("QLineEdit { padding: 4px 8px; font-size: 12px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; }")

            spin_credits = QSpinBox()
            spin_credits.setRange(1, 10)
            spin_credits.setValue(3)
            spin_credits.setFixedHeight(30)
            spin_credits.setFixedWidth(60)
            spin_credits.setStyleSheet("QSpinBox { padding: 2px 4px; font-size: 12px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; }")

            combo_grade = QComboBox()
            grades_scale = [
                ("A (4.0)", 4.0, "A"), ("B+ (3.5)", 3.5, "B+"), ("B (3.0)", 3.0, "B"),
                ("C+ (2.5)", 2.5, "C+"), ("C (2.0)", 2.0, "C"),
                ("D+ (1.5)", 1.5, "D+"), ("D (1.0)", 1.0, "D"), ("F (0.0)", 0.0, "F")
            ]
            for text, val, letter in grades_scale:
                combo_grade.addItem(text, (val, letter))
            combo_grade.setFixedHeight(30)
            combo_grade.setStyleSheet("QComboBox { padding: 2px 8px; font-size: 12px; border: 1px solid #D1D5DB; border-radius: 6px; background: white; }")

            row1.addWidget(edit_course, 4)
            row1.addWidget(_lbl("TC:"))
            row1.addWidget(spin_credits)
            row1.addWidget(_lbl("Điểm chữ:"))
            row1.addWidget(combo_grade, 2)

            # ── Row 1.5: Preset trọng số ──────────────────────────────────────
            PRESETS = {
                "🇻🇳 VN Chuẩn (10-10-20-60)":      (10, 10, 20, 60),
                "🇺🇸 US Typical (15-25-25-35)":    (15, 25, 25, 35),
                "🇬🇧 UK Style (0-40-0-60)":         (0,  40, 0,  60),
                "🎓 Chỉ Cuối kỳ (0-0-0-100)":       (0,  0,  0,  100),
                "⚖️ Đồng đều (25-25-25-25)":        (25, 25, 25, 25),
                "📚 Nghiên cứu (5-5-10-80)":        (5,  5,  10, 80),
                "⚙️ Tùy chỉnh":                     None,
            }

            row_preset = QHBoxLayout()
            row_preset.setSpacing(8)

            preset_combo = QComboBox()
            for preset_name in PRESETS:
                preset_combo.addItem(preset_name)
            preset_combo.setFixedHeight(26)
            preset_combo.setStyleSheet("""
                QComboBox {
                    padding: 2px 8px; font-size: 11px; border: 1px solid #D1D5DB;
                    border-radius: 5px; background: white; color: #374151;
                }
                QComboBox::drop-down { border: none; }
            """)

            def _wspin(val):
                """Weight spinbox (integer %)."""
                sp = QSpinBox()
                sp.setRange(0, 100)
                sp.setSingleStep(5)
                sp.setSuffix("%")
                sp.setValue(val)
                sp.setFixedHeight(26)
                sp.setFixedWidth(62)
                sp.setStyleSheet("QSpinBox { padding: 1px 2px; font-size: 11px; border: 1px solid #D1D5DB; border-radius: 5px; background: white; }")
                return sp

            w_cc  = _wspin(10)
            w_bt  = _wspin(10)
            w_gk  = _wspin(20)
            w_ck  = _wspin(60)

            # Total label — xanh nếu = 100, đỏ nếu ≠ 100
            total_lbl = QLabel("= 100%")
            total_lbl.setFixedHeight(26)
            total_lbl.setStyleSheet(
                "font-size: 11px; font-weight: 800; color: #059669; background: #ECFDF5; "
                "border: 1px solid #A7F3D0; border-radius: 5px; padding: 0 8px;"
            )

            def _update_total(_unused=None):
                total = w_cc.value() + w_bt.value() + w_gk.value() + w_ck.value()
                total_lbl.setText(f"= {total}%")
                if total == 100:
                    total_lbl.setStyleSheet(
                        "font-size: 11px; font-weight: 800; color: #059669; background: #ECFDF5; "
                        "border: 1px solid #A7F3D0; border-radius: 5px; padding: 0 8px;"
                    )
                else:
                    total_lbl.setStyleSheet(
                        "font-size: 11px; font-weight: 800; color: #DC2626; background: #FEF2F2; "
                        "border: 1px solid #FECACA; border-radius: 5px; padding: 0 8px;"
                    )
                # Re-calc T10 with new weights
                _auto_calc_t10()

            def _on_preset_change(idx):
                pname = preset_combo.currentText()
                pval = PRESETS.get(pname)
                if pval is not None:
                    cc_w, bt_w, gk_w, ck_w = pval
                    for sp, v in [(w_cc, cc_w), (w_bt, bt_w), (w_gk, gk_w), (w_ck, ck_w)]:
                        sp.blockSignals(True)
                        sp.setValue(v)
                        sp.blockSignals(False)
                    _update_total()
                # "Tùy chỉnh" → người dùng tự nhập, không làm gì thêm

            preset_combo.currentIndexChanged.connect(_on_preset_change)
            w_cc.valueChanged.connect(_update_total)
            w_bt.valueChanged.connect(_update_total)
            w_gk.valueChanged.connect(_update_total)
            w_ck.valueChanged.connect(_update_total)

            row_preset.addWidget(_lbl("Tỉ lệ:"))
            row_preset.addWidget(preset_combo, 3)
            row_preset.addWidget(_lbl("CC:"))
            row_preset.addWidget(w_cc)
            row_preset.addWidget(_lbl("BT:"))
            row_preset.addWidget(w_bt)
            row_preset.addWidget(_lbl("GK:"))
            row_preset.addWidget(w_gk)
            row_preset.addWidget(_lbl("CK:"))
            row_preset.addWidget(w_ck)
            row_preset.addWidget(total_lbl)
            row_preset.addStretch()

            # ── Row 2: Điểm thành phần + T10 preview + Thêm ──────────────────
            row2 = QHBoxLayout()
            row2.setSpacing(8)

            def _dspin(placeholder):
                sp = QDoubleSpinBox()
                sp.setRange(0.0, 10.0)
                sp.setSingleStep(0.1)
                sp.setDecimals(1)
                sp.setSpecialValueText("--")
                sp.setValue(0.0)
                sp.setFixedHeight(28)
                sp.setFixedWidth(70)
                sp.setStyleSheet("QDoubleSpinBox { padding: 2px 4px; font-size: 11px; border: 1px solid #D1D5DB; border-radius: 5px; background: white; }")
                sp.setToolTip(placeholder)
                return sp

            spin_cc = _dspin("Điểm CC/GVHD")
            spin_bt = _dspin("Điểm Bài Tập")
            spin_gk = _dspin("Điểm Giữa Kỳ")
            spin_ck = _dspin("Điểm Cuối Kỳ")

            # ── Live T10 preview label ─────────────────────────────────────────
            t10_preview_lbl = QLabel("T10: --")
            t10_preview_lbl.setFixedHeight(28)
            t10_preview_lbl.setStyleSheet(
                "font-size: 12px; font-weight: 800; color: #64748B; background: #F1F5F9; "
                "border: 1px solid #CBD5E1; border-radius: 6px; padding: 0 10px;"
            )
            t10_preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # ── Note công thức (cập nhật động) ────────────────────────────────
            note_lbl = QLabel()
            note_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; border: none; background: transparent; padding-top: 2px;")

            def _update_formula_note():
                note_lbl.setText(
                    f"📐 T10 = CC×{w_cc.value()}% + BT×{w_bt.value()}% + GK×{w_gk.value()}% + CK×{w_ck.value()}%"
                    "  |  Bỏ trống thành phần nào → trọng số tự phân bổ lại"
                )

            def _t10_to_letter_idx(t10):
                if t10 >= 8.5: return 0
                if t10 >= 8.0: return 1
                if t10 >= 7.0: return 2
                if t10 >= 6.5: return 3
                if t10 >= 5.5: return 4
                if t10 >= 5.0: return 5
                if t10 >= 4.0: return 6
                return 7

            def _auto_calc_t10(_unused=None):
                """Tự tính T10 từ điểm thành phần với trọng số hiện tại."""
                WEIGHTS = {
                    "cc": w_cc.value() / 100,
                    "bt": w_bt.value() / 100,
                    "gk": w_gk.value() / 100,
                    "ck": w_ck.value() / 100,
                }
                scores = {
                    "cc": spin_cc.value(),
                    "bt": spin_bt.value(),
                    "gk": spin_gk.value(),
                    "ck": spin_ck.value(),
                }
                entered = {k: v for k, v in scores.items() if v > 0}
                _update_formula_note()

                if not entered:
                    t10_preview_lbl.setText("T10: --")
                    t10_preview_lbl.setStyleSheet(
                        "font-size: 12px; font-weight: 800; color: #64748B; background: #F1F5F9; "
                        "border: 1px solid #CBD5E1; border-radius: 6px; padding: 0 10px;"
                    )
                    return

                total_w = sum(WEIGHTS[k] for k in entered)
                if total_w == 0:
                    return
                t10 = round(sum(v * WEIGHTS[k] / total_w for k, v in entered.items()), 2)

                if t10 >= 8.0:   color, bg, border = "#059669", "#ECFDF5", "#A7F3D0"
                elif t10 >= 6.5: color, bg, border = "#2563EB", "#EFF6FF", "#BFDBFE"
                elif t10 >= 5.0: color, bg, border = "#D97706", "#FFFBEB", "#FDE68A"
                else:            color, bg, border = "#DC2626", "#FEF2F2", "#FECACA"

                t10_preview_lbl.setText(f"T10: {t10:.2f}")
                t10_preview_lbl.setStyleSheet(
                    f"font-size: 12px; font-weight: 800; color: {color}; background: {bg}; "
                    f"border: 1px solid {border}; border-radius: 6px; padding: 0 10px;"
                )
                combo_grade.setCurrentIndex(_t10_to_letter_idx(t10))

            spin_cc.valueChanged.connect(_auto_calc_t10)
            spin_bt.valueChanged.connect(_auto_calc_t10)
            spin_gk.valueChanged.connect(_auto_calc_t10)
            spin_ck.valueChanged.connect(_auto_calc_t10)

            # Khởi tạo note lần đầu
            _update_formula_note()

            row2.addWidget(_lbl("CC/GVHD:"))
            row2.addWidget(spin_cc)
            row2.addWidget(_lbl("Bài Tập:"))
            row2.addWidget(spin_bt)
            row2.addWidget(_lbl("Giữa Kỳ:"))
            row2.addWidget(spin_gk)
            row2.addWidget(_lbl("Cuối Kỳ:"))
            row2.addWidget(spin_ck)
            row2.addWidget(t10_preview_lbl)
            row2.addStretch()

            btn_add = QPushButton("+ Thêm Môn")
            btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_add.setFixedHeight(30)
            btn_add.setStyleSheet("""
                QPushButton { background: #1E293B; color: white; border-radius: 6px;
                    font-weight: bold; padding: 0 14px; font-size: 12px; border: none; }
                QPushButton:hover { background: #374151; }
            """)
            btn_add.clicked.connect(
                lambda checked, s=sem_name, c=edit_course, sp=spin_credits, cg=combo_grade,
                       scc=spin_cc, sbt=spin_bt, sgk=spin_gk, sck=spin_ck,
                       wcc=w_cc, wbt=w_bt, wgk=w_gk, wck=w_ck:
                self._add_course_with_weights(s, c, sp, cg, scc, sbt, sgk, sck, wcc, wbt, wgk, wck)
            )
            row2.addWidget(btn_add)

            form_outer.addLayout(row1)
            form_outer.addLayout(row_preset)
            form_outer.addLayout(row2)
            form_outer.addWidget(note_lbl)

            sem_lay.addWidget(form_widget)

            self.semesters_layout.addWidget(sem_frame)

        self.semesters_layout.addStretch()

    def _add_semester_dialog(self):
        text, ok = QInputDialog.getText(self, "Thêm Học Kỳ", "Nhập tên học kỳ (VD: Học kỳ 1 - 2025-2026):")
        if ok and text.strip():
            student = crud.get_current_student()
            if not student: return
            conn = crud.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_grades (student_id, semester, course_name, credits, grade_value, grade_letter)
                VALUES (?, ?, 'Semester Started', 0, 0.0, '')
            ''', (student["id"], text.strip()))
            conn.commit()
            conn.close()
            self.refresh_gpa_manager()

    def _delete_semester(self, semester_name):
        student = crud.get_current_student()
        if not student: return
        conn = crud.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_grades WHERE student_id = ? AND semester = ?", (student["id"], semester_name))
        conn.commit()
        conn.close()
        self.refresh_gpa_manager()

    def _add_course_detailed(self, semester_name, edit_course, spin_credits, combo_grade,
                             spin_cc, spin_bt, spin_gk, spin_ck):
        student = crud.get_current_student()
        if not student: return

        name = edit_course.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên môn học không được để trống.")
            return

        credits = spin_credits.value()
        val, letter = combo_grade.currentData()

        # Get optional score components (0.0 means not entered, treat as None)
        def _get_score(sp):
            if sp is None:
                return None
            v = sp.value()
            return v if v > 0 else None

        cc = _get_score(spin_cc)
        bt = _get_score(spin_bt)
        gk = _get_score(spin_gk)
        ck = _get_score(spin_ck)

        # ── Tính T10 từ công thức nếu có điểm thành phần ─────────────────────
        # Trọng số chuẩn VN: CC=10%, BT=10%, GK=20%, CK=60%
        WEIGHTS = {"cc": 0.10, "bt": 0.10, "gk": 0.20, "ck": 0.60}
        entered = {k: v for k, v in {"cc": cc, "bt": bt, "gk": gk, "ck": ck}.items() if v is not None}

        if entered:
            total_w = sum(WEIGHTS[k] for k in entered)
            t10 = round(sum(v * WEIGHTS[k] / total_w for k, v in entered.items()), 2)

            # Xác định grade_value và letter từ T10 (tự động, không phụ thuộc combo)
            if t10 >= 8.5:    val, letter = 4.0, "A"
            elif t10 >= 8.0:  val, letter = 3.5, "B+"
            elif t10 >= 7.0:  val, letter = 3.0, "B"
            elif t10 >= 6.5:  val, letter = 2.5, "C+"
            elif t10 >= 5.5:  val, letter = 2.0, "C"
            elif t10 >= 5.0:  val, letter = 1.5, "D+"
            elif t10 >= 4.0:  val, letter = 1.0, "D"
            else:             val, letter = 0.0, "F"
        else:
            # Không có điểm thành phần → dùng điểm chữ từ combo, convert sang T10
            t10 = round(val * 10 / 4, 1)

        conn = crud.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM student_grades WHERE student_id = ? AND semester = ? AND course_name = 'Semester Started' AND credits = 0",
            (student["id"], semester_name)
        )
        placeholder = cursor.fetchone()
        if placeholder:
            cursor.execute("DELETE FROM student_grades WHERE id = ?", (placeholder["id"],))
            conn.commit()
        conn.close()

        crud.add_student_grade(student["id"], semester_name, name, credits, val, letter,
                               attempt=1, grade_cc=cc, grade_bt=bt, grade_gk=gk, grade_ck=ck, grade_t10=t10)
        edit_course.clear()
        if spin_cc: spin_cc.setValue(0.0)
        if spin_bt: spin_bt.setValue(0.0)
        if spin_gk: spin_gk.setValue(0.0)
        if spin_ck: spin_ck.setValue(0.0)
        self.refresh_gpa_manager()

    def _add_course_with_weights(self, semester_name, edit_course, spin_credits, combo_grade,
                                 spin_cc, spin_bt, spin_gk, spin_ck,
                                 w_cc, w_bt, w_gk, w_ck):
        """Thêm môn học với trọng số tùy chỉnh từ form."""
        student = crud.get_current_student()
        if not student: return

        name = edit_course.text().strip()
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên môn học không được để trống.")
            return

        credits = spin_credits.value()
        val, letter = combo_grade.currentData()

        def _get_score(sp):
            if sp is None: return None
            v = sp.value()
            return v if v > 0 else None

        cc = _get_score(spin_cc)
        bt = _get_score(spin_bt)
        gk = _get_score(spin_gk)
        ck = _get_score(spin_ck)

        # Dùng trọng số từ weight spinboxes
        WEIGHTS = {
            "cc": (w_cc.value() if w_cc else 10) / 100,
            "bt": (w_bt.value() if w_bt else 10) / 100,
            "gk": (w_gk.value() if w_gk else 20) / 100,
            "ck": (w_ck.value() if w_ck else 60) / 100,
        }
        entered = {k: v for k, v in {"cc": cc, "bt": bt, "gk": gk, "ck": ck}.items() if v is not None}

        if entered:
            total_w = sum(WEIGHTS[k] for k in entered)
            t10 = round(sum(v * WEIGHTS[k] / total_w for k, v in entered.items()), 2) if total_w > 0 else 0.0
            # Xác định grade từ T10
            if t10 >= 8.5:    val, letter = 4.0, "A"
            elif t10 >= 8.0:  val, letter = 3.5, "B+"
            elif t10 >= 7.0:  val, letter = 3.0, "B"
            elif t10 >= 6.5:  val, letter = 2.5, "C+"
            elif t10 >= 5.5:  val, letter = 2.0, "C"
            elif t10 >= 5.0:  val, letter = 1.5, "D+"
            elif t10 >= 4.0:  val, letter = 1.0, "D"
            else:             val, letter = 0.0, "F"
        else:
            t10 = round(val * 10 / 4, 1)

        conn = crud.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM student_grades WHERE student_id = ? AND semester = ? AND course_name = 'Semester Started' AND credits = 0",
            (student["id"], semester_name)
        )
        placeholder = cursor.fetchone()
        if placeholder:
            cursor.execute("DELETE FROM student_grades WHERE id = ?", (placeholder["id"],))
            conn.commit()
        conn.close()

        crud.add_student_grade(student["id"], semester_name, name, credits, val, letter,
                               attempt=1, grade_cc=cc, grade_bt=bt, grade_gk=gk, grade_ck=ck, grade_t10=t10)
        edit_course.clear()
        if spin_cc: spin_cc.setValue(0.0)
        if spin_bt: spin_bt.setValue(0.0)
        if spin_gk: spin_gk.setValue(0.0)
        if spin_ck: spin_ck.setValue(0.0)
        self.refresh_gpa_manager()

    def _add_course(self, semester_name, edit_course, spin_credits, combo_grade):
        """Legacy wrapper kept for compatibility."""
        self._add_course_detailed(semester_name, edit_course, spin_credits, combo_grade,
                                  None, None, None, None)

    def _delete_course(self, grade_id):
        crud.delete_student_grade(grade_id)
        self.refresh_gpa_manager()
