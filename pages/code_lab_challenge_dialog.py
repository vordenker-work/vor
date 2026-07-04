from core.translation.base_translatable_widget import make_translatable, BaseTranslatableWidget, BaseTranslatableFrame, BaseTranslatableDialog
from core.translation.translator import Translator
import json
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QMessageBox, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import code_lab_db

class AddChallengeDialog(BaseTranslatableDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.translate("title.add_new_programming"))
        self.resize(520, 720)
        self.test_cases_rows = []

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #0F172A;
            }
            QLabel {
                color: #475569;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #2563EB;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #EFF6FF;
                selection-color: #2563EB;
                border: 1px solid #CBD5E1;
            }
            QScrollArea {
                border: 1px solid #E2E8F0;
                background-color: #F8FAFC;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
            QPushButton#btnPrimary {
                background-color: #2563EB;
                color: white;
                border: none;
            }
            QPushButton#btnPrimary:hover {
                background-color: #1D4ED8;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        main_scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(scroll_content)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # 1. Challenge Title
        self.layout.addWidget(make_translatable(QLabel(), "dialog.challenge_title"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(Translator.translate("placeholder.eg_find_maximum")); self.title_input.placeholder_translation_key = "placeholder.eg_find_maximum"
        self.layout.addWidget(self.title_input)

        # 2. Topic/Category
        self.layout.addWidget(make_translatable(QLabel(), "dialog.topiccategory"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText(Translator.translate("placeholder.eg_array_math")); self.topic_input.placeholder_translation_key = "placeholder.eg_array_math"
        self.layout.addWidget(self.topic_input)

        # 3. Difficulty
        self.layout.addWidget(make_translatable(QLabel(), "dialog.difficulty_level"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Medium", "Hard"])
        self.layout.addWidget(self.diff_combo)

        # 4. Description (HTML supported)
        self.layout.addWidget(make_translatable(QLabel(), "dialog.description_html_supported"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(Translator.translate("placeholder.write_details_here")); self.desc_input.placeholder_translation_key = "placeholder.write_details_here"
        self.desc_input.setMinimumHeight(100)
        self.layout.addWidget(self.desc_input)

        # 5. Starter Code
        self.layout.addWidget(make_translatable(QLabel(), "dialog.starter_code_template"))
        self.starter_input = QTextEdit()
        self.starter_input.setFont(QFont("Consolas", 11))
        self.starter_input.setPlaceholderText(Translator.translate("placeholder.def_findmaxnumsn_write")); self.starter_input.placeholder_translation_key = "placeholder.def_findmaxnumsn_write"
        self.starter_input.setMinimumHeight(120)
        self.layout.addWidget(self.starter_input)

        # 6. Test Cases Section
        self.layout.addWidget(make_translatable(QLabel(), "dialog.test_cases_inputs"))
        
        # Header Row
        header_widget = QWidget()
        header_lay = QHBoxLayout(header_widget)
        header_lay.setContentsMargins(0, 0, 0, 0)
        header_lay.setSpacing(8)
        lbl_in = make_translatable(QLabel(), "dialog.input_args_json")
        lbl_in.setStyleSheet("color: #64748B; font-size: 11px;")
        lbl_out = make_translatable(QLabel(), "dialog.expected_output_json")
        lbl_out.setStyleSheet("color: #64748B; font-size: 11px;")
        header_lay.addWidget(lbl_in, 2)
        header_lay.addWidget(lbl_out, 1)
        header_lay.addSpacing(44) # spacer for delete button alignment
        self.layout.addWidget(header_widget)

        # Container for dynamic test case rows
        self.cases_container = QWidget()
        self.cases_layout = QVBoxLayout(self.cases_container)
        self.cases_layout.setContentsMargins(0, 0, 0, 0)
        self.cases_layout.setSpacing(8)
        self.layout.addWidget(self.cases_container)

        # Add Test Case button
        self.btn_add_case = make_translatable(QPushButton(), "dialog.add_test_case")
        self.btn_add_case.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_case.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #2563EB;
                border: 1px dashed #CBD5E1;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                border: 1px dashed #2563EB;
                color: #1D4ED8;
            }
        """)
        self.btn_add_case.clicked.connect(self.add_test_case_row)
        self.layout.addWidget(self.btn_add_case)

        # Add first row by default
        self.add_test_case_row()

        main_scroll.setWidget(scroll_content)
        outer_layout.addWidget(main_scroll)

        # Dialog Action Buttons Footer
        footer = QFrame()
        footer.setStyleSheet("QFrame { background-color: #F8FAFC; border-top: 1px solid #E2E8F0; }")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setSpacing(12)
        
        footer_layout.addStretch()
        
        self.btn_cancel = make_translatable(QPushButton(), "button.cancel")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(self.btn_cancel)
        
        self.btn_save = make_translatable(QPushButton(), "dialog.save_challenge")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.btn_save.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_save)
        
        outer_layout.addWidget(footer)
        
        from core.config import apply_theme
        apply_theme(self)

    def add_test_case_row(self, input_val="", output_val=""):
        row_widget = QWidget()
        row_lay = QHBoxLayout(row_widget)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(8)
        
        input_input = QLineEdit()
        input_input.setPlaceholderText(Translator.translate("placeholder.eg_1_5"))
        input_input.setText(input_val)
        
        output_input = QLineEdit()
        output_input.setPlaceholderText(Translator.translate("placeholder.eg_5"))
        output_input.setText(output_val)
        
        btn_del = QPushButton("🗑️")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFixedWidth(36)
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        
        row_lay.addWidget(input_input, 2)
        row_lay.addWidget(output_input, 1)
        row_lay.addWidget(btn_del)
        
        self.cases_layout.addWidget(row_widget)
        
        row_data = {
            "widget": row_widget,
            "input": input_input,
            "output": output_input
        }
        self.test_cases_rows.append(row_data)
        
        btn_del.clicked.connect(lambda: self.remove_test_case_row(row_data))

    def remove_test_case_row(self, row_data):
        if len(self.test_cases_rows) <= 1:
            QMessageBox.warning(self, Translator.translate("msg.title.validation_error"), Translator.translate("msg.text.you_must_keep"))
            return
            
        self.test_cases_rows.remove(row_data)
        row_data["widget"].deleteLater()

    def accept(self):
        title = self.title_input.text().strip()
        topic = self.topic_input.text().strip()
        diff = self.diff_combo.currentText()
        desc = self.desc_input.toPlainText().strip()
        starter = self.starter_input.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, Translator.translate("msg.title.validation_error"), Translator.translate("msg.text.challenge_title_cannot"))
            return
        if not topic:
            QMessageBox.warning(self, Translator.translate("msg.title.validation_error"), Translator.translate("msg.text.topic_cannot_be"))
            return
        if not desc:
            QMessageBox.warning(self, Translator.translate("msg.title.validation_error"), Translator.translate("msg.text.description_cannot_be"))
            return
        if not starter:
            QMessageBox.warning(self, Translator.translate("msg.title.validation_error"), Translator.translate("msg.text.starter_code_cannot"))
            return
            
        parsed_cases = []
        for idx, row in enumerate(self.test_cases_rows):
            in_text = row["input"].text().strip()
            out_text = row["output"].text().strip()
            
            if not in_text or not out_text:
                QMessageBox.warning(self, "Validation Error", f"Test case {idx + 1} has empty fields.")
                return
                
            try:
                in_json = json.loads(in_text)
                if not isinstance(in_json, list):
                    QMessageBox.warning(
                        self, 
                        "Validation Error", 
                        f"Test case {idx + 1} Input must be a valid JSON List (representing function arguments).\nExample: [2, 3] or [[1, 5, 3]]"
                    )
                    return
            except Exception:
                QMessageBox.warning(self, "Validation Error", f"Test case {idx + 1} Input is not valid JSON.\nExample: [2, 3] or [\"hello\"]")
                return
                
            try:
                out_json = json.loads(out_text)
            except Exception:
                QMessageBox.warning(self, "Validation Error", f"Test case {idx + 1} Expected Output is not valid JSON.\nExample: 5 or \"olleh\" or true")
                return
                
            parsed_cases.append({
                "input": in_json,
                "output": out_json
            })
            
        base_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if not base_id:
            base_id = "custom-challenge"
            
        challenge_id = base_id
        counter = 1
        while code_lab_db.get_challenge_by_id(challenge_id) is not None:
            challenge_id = f"{base_id}-{counter}"
            counter += 1
            
        try:
            code_lab_db.add_custom_challenge(
                challenge_id,
                title,
                topic,
                diff,
                desc,
                starter,
                json.dumps(parsed_cases)
            )
            QMessageBox.information(self, "Success", f"Challenge '{title}' added successfully!")
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save challenge to database:\n{str(e)}")
