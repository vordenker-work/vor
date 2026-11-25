from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QGridLayout, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .components import ShadowCard, SkillChip, ProjectCard, TimelineItem
from database import crud

class ProfilePortfolioTab(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.parent_page = parent
        self.controller = controller
        
        layout = QVBoxLayout(self)
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

    def refresh(self):
        self._clear_layout(self.workspace_layout)
        self.init_hero_section()
        self.init_skills_achievements()
        self.init_portfolio()
        self.init_timelines()
        self.init_activity()

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

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
        total_focus_hours = 0.0
        if student:
            is_dirty = student.get("context", {}).get("is_dirty", 0) or student.get("is_dirty", 0)
            status_text = student.get("context", {}).get("ai_status", "EMPTY")
            updated_at = student.get("context", {}).get("updated_at", "")[:19].replace("T", " ")
            
            raw_input = student.get("context", {}).get("raw_input", {})
            if isinstance(raw_input, dict) and isinstance(raw_input.get("academic_context"), dict):
                sessions = raw_input.get("academic_context", {}).get("study_sessions", [])
                if isinstance(sessions, list):
                    total_minutes = sum(int(s.get("minutes", 0)) for s in sessions if isinstance(s, dict))
                    total_focus_hours = total_minutes / 60.0
            
        sync_status = "Pending Sync" if is_dirty else "Synchronized with Backend"
        
        for text, time in [
            (f"AI Plan Status: {status_text}", updated_at),
            (f"Local SQLite Sync Status: {sync_status}", "Realtime"),
            (f"Focused Study Logged: {total_focus_hours:.2f} hours", "Realtime")
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

    def _trigger_ai_plan_from_portfolio(self):
        if self.controller and hasattr(self.controller, "show_page"):
            self.controller.show_page(0)
            dashboard_page = self.controller.pages_container.widget(0)
            if dashboard_page and hasattr(dashboard_page, "start_generation"):
                dashboard_page.start_generation()
