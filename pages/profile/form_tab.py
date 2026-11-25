from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QLineEdit, QTextEdit, QComboBox, QMessageBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from .components import ShadowCard, TimetableEditor
from database import crud
from core.i18n import _

class ProfileFormTab(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.parent_page = parent
        self.controller = controller
        
        layout = QVBoxLayout(self)
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
        form_scroll.verticalScrollBar().setSingleStep(15) 

        layout.addWidget(form_scroll)

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

    def load_data(self, student):
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
