import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSplitter, QTabWidget, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from database import crud
from .components import ShadowCard
from .form_tab import ProfileFormTab
from .portfolio_tab import ProfilePortfolioTab
from .gpa_tab import GPAManagerTab

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
        self.form_tab = ProfileFormTab(parent=self, controller=self.controller)
        self.tabs.addTab(self.form_tab, "Academic Profile Form")
        
        # 2. Tab 2: Portfolio View (Scrollable workspace)
        self.portfolio_tab = ProfilePortfolioTab(parent=self, controller=self.controller)
        self.tabs.addTab(self.portfolio_tab, "AI Academic Plan")
        
        # 3. Tab 3: GPA Manager
        self.gpa_tab = GPAManagerTab(parent=self, controller=self.controller)
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
        gpa_val = "0.00"
        readiness_val = "0%"
        if student:
            gpa_raw = student.get("context", {}).get("raw_input", {}).get("student_info", {}).get("gpa", 0.0)
            try:
                gpa_val = f"{float(gpa_raw):.2f}"
            except:
                gpa_val = "0.00"
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

    def load_data(self):
        student = crud.get_current_student()
        if not student:
            return
            
        display_name = student.get("display_name", "") or ""
        
        # Load sub-tab form data
        self.form_tab.load_data(student)
        
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
        self.gpa_tab.refresh_gpa_manager()
        self.portfolio_tab.refresh()
        
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
