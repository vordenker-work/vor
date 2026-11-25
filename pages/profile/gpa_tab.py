from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QLineEdit, 
                             QComboBox, QMessageBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, 
                             QDoubleSpinBox, QSpinBox, QInputDialog, QDialog,
                             QTextBrowser, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient

from .components import ShadowCard
from database import crud

class GPAManagerTab(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.parent_page = parent
        self.controller = controller
        
        gpa_layout = QVBoxLayout(self)
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

        # Add Semester & GPA Simulator button card
        btn_card = ShadowCard(radius=14)
        btn_card.layout.setSpacing(8)
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

        self.btn_gpa_simulator = QPushButton("🎯 Giả Lập GPA")
        self.btn_gpa_simulator.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gpa_simulator.setStyleSheet("""
            QPushButton {
                background: #059669; color: white; border-radius: 8px; font-weight: bold;
                padding: 10px 18px; font-size: 13px; border: none;
            }
            QPushButton:hover { background: #047857; }
        """)
        self.btn_gpa_simulator.clicked.connect(self._show_gpa_simulator_dialog)
        btn_card.layout.addWidget(self.btn_gpa_simulator)
        
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
        
        # Update the GPA field in Form tab if it exists
        if self.parent_page and hasattr(self.parent_page, "form_tab") and hasattr(self.parent_page.form_tab, "edit_gpa"):
            self.parent_page.form_tab.edit_gpa.setText(f"{cum_gpa:.2f}")
            
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

        def _get_score(sp):
            if sp is None:
                return None
            v = sp.value()
            return v if v > 0 else None

        cc = _get_score(spin_cc)
        bt = _get_score(spin_bt)
        gk = _get_score(spin_gk)
        ck = _get_score(spin_ck)

        WEIGHTS = {"cc": 0.10, "bt": 0.10, "gk": 0.20, "ck": 0.60}
        entered = {k: v for k, v in {"cc": cc, "bt": bt, "gk": gk, "ck": ck}.items() if v is not None}

        if entered:
            total_w = sum(WEIGHTS[k] for k in entered)
            t10 = round(sum(v * WEIGHTS[k] / total_w for k, v in entered.items()), 2)

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

    def _add_course_with_weights(self, semester_name, edit_course, spin_credits, combo_grade,
                                 spin_cc, spin_bt, spin_gk, spin_ck,
                                 w_cc, w_bt, w_gk, w_ck):
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
        self._add_course_detailed(semester_name, edit_course, spin_credits, combo_grade,
                                  None, None, None, None)

    def _delete_course(self, grade_id):
        crud.delete_student_grade(grade_id)
        self.refresh_gpa_manager()

    def _show_gpa_simulator_dialog(self):
        student = crud.get_current_student()
        if not student:
            return
        student_id = student["id"]
        grades = crud.get_student_grades(student_id)
        
        cum_gpa, _ = crud.calculate_gpa(student_id)
        
        valid_all = [g for g in grades if not (g["course_name"] == "Semester Started" and g["credits"] == 0)]
        total_credits = sum(g["credits"] for g in valid_all)
        
        dialog = GPASimulatorDialog(cum_gpa, total_credits, self)
        dialog.exec()

class GPASimulatorDialog(QDialog):
    def __init__(self, current_gpa, current_credits, parent=None):
        super().__init__(parent)
        self.current_gpa = current_gpa
        self.current_credits = current_credits
        self.setWindowTitle("Giả lập Mục tiêu GPA")
        self.resize(500, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #0F172A;
                font-family: 'Segoe UI', Arial;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("🎯 Giả Lập Mục Tiêu GPA")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #0F172A;")
        layout.addWidget(header)
        
        # Info card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        info_layout = QGridLayout(info_card)
        info_layout.setContentsMargins(16, 16, 16, 16)
        info_layout.setSpacing(12)
        
        info_layout.addWidget(QLabel("GPA Tích Lũy Hiện Tại:"), 0, 0)
        curr_gpa_val = QLabel(f"<b>{self.current_gpa:.2f}</b>")
        curr_gpa_val.setStyleSheet("font-size: 14px; color: #1E293B;")
        info_layout.addWidget(curr_gpa_val, 0, 1)
        
        info_layout.addWidget(QLabel("Tín Chỉ Đã Tích Lũy:"), 1, 0)
        curr_credits_val = QLabel(f"<b>{self.current_credits}</b>")
        curr_credits_val.setStyleSheet("font-size: 14px; color: #1E293B;")
        info_layout.addWidget(curr_credits_val, 1, 1)
        
        layout.addWidget(info_card)
        
        # Target Form card
        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)
        
        # Target GPA
        form_layout.addWidget(QLabel("Mục Tiêu GPA Tích Lũy:"), 0, 0)
        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(0.0, 4.0)
        self.target_spin.setSingleStep(0.1)
        self.target_spin.setDecimals(2)
        self.target_spin.setValue(min(4.0, self.current_gpa + 0.2))
        self.target_spin.setFixedHeight(30)
        self.target_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 4px 8px; border: 1px solid #CBD5E1; border-radius: 6px; background: white;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #38BDF8;
            }
        """)
        form_layout.addWidget(self.target_spin, 0, 1)
        
        # Expected Credits
        form_layout.addWidget(QLabel("Số Tín Chỉ Học Thêm:"), 1, 0)
        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(1, 150)
        self.credits_spin.setValue(15)
        self.credits_spin.setFixedHeight(30)
        self.credits_spin.setStyleSheet("""
            QSpinBox {
                padding: 4px 8px; border: 1px solid #CBD5E1; border-radius: 6px; background: white;
            }
            QSpinBox:focus {
                border: 1px solid #38BDF8;
            }
        """)
        form_layout.addWidget(self.credits_spin, 1, 1)
        
        layout.addWidget(form_card)
        
        # Result Card
        self.result_card = QFrame()
        self.result_card.setStyleSheet("""
            QFrame {
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        res_layout = QVBoxLayout(self.result_card)
        res_layout.setContentsMargins(16, 16, 16, 16)
        res_layout.setSpacing(10)
        
        res_header = QHBoxLayout()
        res_header.addWidget(QLabel("<b>GPA Cần Đạt Cho Môn Mới:</b>"))
        self.result_gpa_lbl = QLabel("--")
        self.result_gpa_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #2563EB;")
        res_header.addStretch()
        res_header.addWidget(self.result_gpa_lbl)
        res_layout.addLayout(res_header)
        
        self.info_lbl = QLabel("")
        self.info_lbl.setWordWrap(True)
        self.info_lbl.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.4;")
        res_layout.addWidget(self.info_lbl)
        
        layout.addWidget(self.result_card)
        
        # Scenarios Box
        self.scenario_box = QFrame()
        self.scenario_box.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        sc_layout = QVBoxLayout(self.scenario_box)
        sc_layout.setContentsMargins(16, 16, 16, 16)
        sc_layout.setSpacing(8)
        
        sc_title = QLabel("💡 Gợi Ý Kịch Bản Đạt Mục Tiêu")
        sc_title.setStyleSheet("font-weight: bold; color: #0F172A; font-size: 14px;")
        sc_layout.addWidget(sc_title)
        
        self.scenario_text = QTextBrowser()
        self.scenario_text.setFrameShape(QFrame.Shape.NoFrame)
        self.scenario_text.setFixedHeight(150)
        self.scenario_text.setStyleSheet("background: transparent; color: #334155; font-size: 13px;")
        sc_layout.addWidget(self.scenario_text)
        
        layout.addWidget(self.scenario_box)
        
        # Close Button
        close_btn = QPushButton("Đóng")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedHeight(35)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #1E293B; color: white; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover {
                background: #334155;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        # Connect changes
        self.target_spin.valueChanged.connect(self.update_simulation)
        self.credits_spin.valueChanged.connect(self.update_simulation)
        
        self.update_simulation()
        
    def update_simulation(self):
        target_gpa = self.target_spin.value()
        add_credits = self.credits_spin.value()
        
        current_gpa = self.current_gpa
        current_credits = self.current_credits
        
        if add_credits <= 0:
            self.result_gpa_lbl.setText("--")
            self.scenario_box.setVisible(False)
            return
            
        if current_credits == 0:
            req_gpa = target_gpa
        else:
            req_gpa = (target_gpa * (current_credits + add_credits) - current_gpa * current_credits) / add_credits
        
        if current_gpa >= target_gpa and current_credits > 0:
            self.result_gpa_lbl.setText("0.00")
            self.result_gpa_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #059669;")
            self.info_lbl.setText(f"Chúc mừng! GPA tích lũy hiện tại của bạn ({current_gpa:.2f}) đã đạt hoặc vượt qua điểm mục tiêu ({target_gpa:.2f}).")
            self.scenario_box.setVisible(False)
        elif req_gpa > 4.0:
            self.result_gpa_lbl.setText(f"{req_gpa:.2f}")
            self.result_gpa_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #EF4444;")
            self.info_lbl.setText("Mục tiêu quá cao! Bạn không thể đạt được mục tiêu này kể cả khi tất cả môn học mới đều đạt điểm A (4.0). Hãy thử giảm điểm mục tiêu hoặc tăng số tín chỉ học thêm.")
            self.scenario_box.setVisible(False)
        else:
            final_req = max(0.0, req_gpa)
            self.result_gpa_lbl.setText(f"{final_req:.2f}")
            self.result_gpa_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #2563EB;")
            self.info_lbl.setText(f"Để đạt mục tiêu GPA {target_gpa:.2f}, các môn học mới (tổng {add_credits} tín chỉ) cần đạt điểm trung bình tối thiểu là <b>{final_req:.2f}</b>.")
            self.scenario_box.setVisible(True)
            self.generate_scenarios(final_req, add_credits)
            
    def generate_scenarios(self, req_gpa, add_credits):
        course_credits = 3
        M = round(add_credits / course_credits)
        if M <= 0:
            M = 1
            
        valid_combinations = []
        for a in range(M + 1):
            for b_plus in range(M - a + 1):
                for b in range(M - a - b_plus + 1):
                    for c_plus in range(M - a - b_plus - b + 1):
                        c = M - a - b_plus - b - c_plus
                        score = (a * 4.0 + b_plus * 3.5 + b * 3.0 + c_plus * 2.5 + c * 2.0)
                        if score >= req_gpa * M:
                            valid_combinations.append((a, b_plus, b, c_plus, c))
                            
        if not valid_combinations:
            self.scenario_text.setHtml("<p>Cần tất cả các môn mới đạt điểm A (4.0).</p>")
            return
            
        valid_combinations.sort(key=lambda x: (x[0]*4.0 + x[1]*3.5 + x[2]*3.0 + x[3]*2.5 + x[4]*2.0))
        
        safe_comb = max(valid_combinations, key=lambda x: x[0])
        min_comb = valid_combinations[0]
        balanced_comb = max(valid_combinations, key=lambda x: x[1])
        
        def format_comb(comb):
            parts = []
            if comb[0] > 0: parts.append(f"<b>{comb[0]}</b> môn <span style='color: #059669; font-weight: bold;'>A</span>")
            if comb[1] > 0: parts.append(f"<b>{comb[1]}</b> môn <span style='color: #2563EB; font-weight: bold;'>B+</span>")
            if comb[2] > 0: parts.append(f"<b>{comb[2]}</b> môn <span style='color: #2563EB; font-weight: bold;'>B</span>")
            if comb[3] > 0: parts.append(f"<b>{comb[3]}</b> môn <span style='color: #D97706; font-weight: bold;'>C+</span>")
            if comb[4] > 0: parts.append(f"<b>{comb[4]}</b> môn <span style='color: #D97706; font-weight: bold;'>C</span>")
            if not parts:
                return "Tất cả các môn qua môn (từ D trở lên)"
            return ", ".join(parts)
            
        html = f"""
        <div style='line-height: 1.5;'>
            <p><b>Giả định học thêm khoảng {M} môn học (3 tín chỉ/môn):</b></p>
            <ul>
                <li>🟢 <b>Kịch bản An toàn (Điểm cao):</b> {format_comb(safe_comb)}</li>
                <li>🔵 <b>Kịch bản Đồng đều:</b> {format_comb(balanced_comb)}</li>
                <li>🟡 <b>Kịch bản Tối thiểu (Vừa đủ):</b> {format_comb(min_comb)}</li>
            </ul>
        </div>
        """
        self.scenario_text.setHtml(html)
