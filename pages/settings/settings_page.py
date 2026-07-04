from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy, QGridLayout, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from ui_core.components import SaaSCard, ModernSwitch
from database import crud
from core.translation.base_translatable_widget import make_translatable, BaseTranslatableWidget
from core.translation.translator import Translator

class SettingsPage(BaseTranslatableWidget):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setStyleSheet("background-color: #F8FAFC;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._setup_header()
        
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(24)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- Two Column Layout ---
        left_col = QVBoxLayout()
        left_col.setSpacing(24)
        left_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        right_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        left_col.addWidget(self._create_profile_card())
        left_col.addWidget(self._create_preferences_card())
        
        right_col.addWidget(self._create_language_card())
        right_col.addWidget(self._create_sync_card())
        right_col.addWidget(self._create_danger_zone_card())
        
        self.content_layout.addLayout(left_col, 1)
        self.content_layout.addLayout(right_col, 1)
        
        self.main_layout.addWidget(self.content_container, stretch=1)
        self.retranslate_ui()
        
    def _setup_header(self):
        header = QFrame()
        header.setFixedHeight(84)
        header.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        
        info = QVBoxLayout()
        info.setSpacing(4)
        info.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #0F172A; border: none;")
        
        self.sub_lbl = QLabel()
        self.sub_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #64748B; border: none;")
        
        info.addWidget(self.title_lbl)
        info.addWidget(self.sub_lbl)
        layout.addLayout(info)
        layout.addStretch()
        
        self.main_layout.addWidget(header)
        
    def _create_profile_card(self):
        card = SaaSCard(self)
        layout = card.internal_layout
        
        self.profile_title_lbl = QLabel()
        self.profile_title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        layout.addWidget(self.profile_title_lbl)
        layout.addSpacing(8)
        
        student = crud.get_current_student()
        email_str = student.get("email", "Unknown") if student else "Not logged in"
        name_str = student.get("name", "Student") if student else "Guest User"
        display_name = student.get("display_name", name_str) if student else "Guest"
        
        # Profile Row
        prof_row = QHBoxLayout()
        prof_row.setSpacing(16)
        
        avatar = QLabel(name_str[0].upper() if name_str else "?")
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38BDF8, stop:1 #0284C7);
            color: white; border-radius: 28px; font-weight: 900; font-size: 22px;
        """)
        
        info_v = QVBoxLayout()
        n_lbl = QLabel(display_name)
        n_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #0F172A; background: transparent;")
        e_lbl = QLabel(email_str)
        e_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #64748B; background: transparent;")
        info_v.addWidget(n_lbl)
        info_v.addWidget(e_lbl)
        
        prof_row.addWidget(avatar)
        prof_row.addLayout(info_v)
        prof_row.addStretch()
        
        self.btn_edit_profile = QPushButton()
        self.btn_edit_profile.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_profile.setStyleSheet("""
            QPushButton { background: white; color: #0F172A; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 12px; font-weight: 600; font-size: 12px; }
            QPushButton:hover { background: #F8FAFC; }
        """)
        if self.controller and hasattr(self.controller, 'show_page'):
            self.btn_edit_profile.clicked.connect(lambda: self.controller.show_page("ProfilePage"))
        prof_row.addWidget(self.btn_edit_profile, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(prof_row)
        return card

    def _create_preferences_card(self):
        card = SaaSCard(self)
        layout = card.internal_layout
        
        self.pref_title_lbl = QLabel()
        self.pref_title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        layout.addWidget(self.pref_title_lbl)
        
        def add_toggle(text, subtext, default_state=True):
            row = QHBoxLayout()
            row.setContentsMargins(0, 8, 0, 8)
            v = QVBoxLayout()
            t = QLabel(text)
            t.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155; background: transparent;")
            s = QLabel(subtext)
            s.setStyleSheet("font-size: 12px; color: #94A3B8; background: transparent;")
            v.addWidget(t)
            v.addWidget(s)
            
            toggle = ModernSwitch(active_color="#10B981")
            toggle.set_checked(default_state)
            
            row.addLayout(v)
            row.addStretch()
            row.addWidget(toggle, alignment=Qt.AlignmentFlag.AlignVCenter)
            layout.addLayout(row)

        layout.addSpacing(8)
        add_toggle("Push Notifications", "Receive alerts for mock interview reminders.", True)
        add_toggle("Hardware Acceleration", "Use GPU to render Neumorphic shadows smoothly.", True)
        add_toggle("Compact Mode", "Reduce spacing and paddings in UI lists.", False)
        
        return card

    def _create_language_card(self):
        card = SaaSCard(self)
        layout = card.internal_layout
        
        self.lang_title_lbl = QLabel()
        self.lang_title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        layout.addWidget(self.lang_title_lbl)
        layout.addSpacing(12)
        
        self.radio_en = make_translatable(QRadioButton(), "settings.lang.en")
        self.radio_en.setStyleSheet("QRadioButton { font-size: 13px; color: #334155; font-weight: 500; background: transparent; }")
        self.radio_en.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.radio_vi = make_translatable(QRadioButton(), "settings.lang.vi")
        self.radio_vi.setStyleSheet("QRadioButton { font-size: 13px; color: #334155; font-weight: 500; background: transparent; }")
        self.radio_vi.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(self.radio_en)
        layout.addWidget(self.radio_vi)
        
        # Select active language
        current_lang = Translator.current_language()
        if current_lang == "vi":
            self.radio_vi.setChecked(True)
        else:
            self.radio_en.setChecked(True)
            
        # Bind toggle actions
        self.radio_en.toggled.connect(lambda checked: checked and self._change_lang("en"))
        self.radio_vi.toggled.connect(lambda checked: checked and self._change_lang("vi"))
        
        return card

    def _change_lang(self, lang_code):
        Translator.set_language(lang_code)

    def _create_sync_card(self):
        card = SaaSCard(self)
        layout = card.internal_layout
        
        self.sync_title_lbl = QLabel()
        self.sync_title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #0F172A; background: transparent; border: none;")
        layout.addWidget(self.sync_title_lbl)
        layout.addSpacing(12)
        
        self.sync_desc_lbl = QLabel()
        self.sync_desc_lbl.setWordWrap(True)
        self.sync_desc_lbl.setStyleSheet("color: #64748B; font-size: 13px; line-height: 1.5; background: transparent;")
        layout.addWidget(self.sync_desc_lbl)
        
        layout.addSpacing(16)
        status_box = QFrame()
        status_box.setStyleSheet("background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px;")
        sb_layout = QHBoxLayout(status_box)
        sb_layout.setContentsMargins(16, 12, 16, 12)
        
        icon = QLabel("●")
        icon.setStyleSheet("color: #16A34A; font-size: 14px; background: transparent; border: none;")
        
        self.sync_status_lbl = QLabel()
        self.sync_status_lbl.setStyleSheet("color: #16A34A; font-size: 13px; font-weight: 700; background: transparent; border: none;")
        
        sb_layout.addWidget(icon)
        sb_layout.addWidget(self.sync_status_lbl)
        sb_layout.addStretch()
        
        layout.addWidget(status_box)
        return card

    def _create_danger_zone_card(self):
        card = SaaSCard(self)
        card.setStyleSheet(card.styleSheet() + " #SaaSCard { border: 1px solid #FECACA; }")
        layout = card.internal_layout
        
        self.danger_title_lbl = QLabel()
        self.danger_title_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #DC2626; background: transparent; border: none;")
        layout.addWidget(self.danger_title_lbl)
        layout.addSpacing(12)
        
        self.danger_desc_lbl = QLabel()
        self.danger_desc_lbl.setStyleSheet("color: #64748B; font-size: 13px; background: transparent;")
        layout.addWidget(self.danger_desc_lbl)
        
        layout.addSpacing(16)
        
        self.btn_clear_cache = QPushButton()
        self.btn_clear_cache.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_cache.setStyleSheet("""
            QPushButton { background: white; color: #DC2626; border: 1px solid #FECACA; border-radius: 6px; padding: 10px 16px; font-weight: 700; font-size: 13px; text-align: left; }
            QPushButton:hover { background: #FEF2F2; }
        """)
        
        self.btn_logout = QPushButton()
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton { background: #EF4444; color: white; border: none; border-radius: 6px; padding: 10px 16px; font-weight: 700; font-size: 13px; text-align: left; }
            QPushButton:hover { background: #DC2626; }
        """)
        self.btn_logout.clicked.connect(self._handle_logout)
        
        layout.addWidget(self.btn_clear_cache)
        layout.addWidget(self.btn_logout)
        
        return card

    def _handle_logout(self):
        if self.controller and hasattr(self.controller, 'logout'):
            self.controller.logout()

    def retranslate_ui(self):
        """Retranslates all visible texts in SettingsPage on language changed."""
        self.title_lbl.setText(Translator.translate("settings.title", "Settings & Preferences"))
        self.sub_lbl.setText(Translator.translate("settings.description", "Manage your account, UI preferences, and local data sync."))
        
        self.profile_title_lbl.setText(Translator.translate("settings.section.profile", "Account Profile"))
        self.pref_title_lbl.setText(Translator.translate("settings.section.preferences", "UI & Preferences"))
        self.lang_title_lbl.setText(Translator.translate("settings.section.language", "Language / Ngôn ngữ"))
        self.sync_title_lbl.setText(Translator.translate("settings.section.sync", "System & Data Sync"))
        self.danger_title_lbl.setText(Translator.translate("settings.section.danger", "Danger Zone"))
        
        self.sync_desc_lbl.setText(Translator.translate("settings.sync.description", "VOR uses a Local-First architecture. Your AI plans and CVs are saved locally in SQLite and synchronized in the background to the cloud."))
        self.sync_status_lbl.setText(Translator.translate("settings.sync.status", "Background Sync is Active"))
        self.danger_desc_lbl.setText(Translator.translate("settings.danger.description", "These actions cannot be undone. Please be certain before proceeding."))
        
        self.btn_edit_profile.setText(Translator.translate("settings.btn.edit_profile", "Edit Profile"))
        self.btn_clear_cache.setText(Translator.translate("settings.btn.clear_cache", "Clear Local Cache"))
        self.btn_logout.setText(Translator.translate("settings.btn.logout", "Log Out of Session"))
