import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QComboBox,
                             QGraphicsDropShadowEffect, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

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
