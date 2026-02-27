# -*- coding: utf-8 -*-
"""
导入对话框组件 - Windows 7兼容版本
包含ImportThread和ImportDialog类
白底黑字风格
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QProgressBar, QFrame, QMessageBox,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QFontDatabase


class ImportThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str, int, int)

    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        try:
            from medicines_data_300 import medicines_300

            total = len(medicines_300)
            added = 0
            updated = 0

            for i, medicine in enumerate(medicines_300):
                try:
                    existing = self.db.fetchone(
                        "SELECT id FROM medicines WHERE name = ?",
                        (medicine['name'],)
                    )

                    if existing:
                        self.db.execute('''
                            UPDATE medicines 
                            SET alias=?, category=?, nature=?, taste=?, meridian=?,
                                efficacy=?, indications=?, usage=?, dosage=?, 
                                contraindication=?, notes=?
                            WHERE id=?
                        ''', (
                            medicine.get('alias', ''),
                            medicine.get('category', ''),
                            medicine.get('nature', ''),
                            medicine.get('taste', ''),
                            medicine.get('meridian', ''),
                            medicine.get('efficacy', ''),
                            medicine.get('indications', ''),
                            medicine.get('usage', ''),
                            medicine.get('dosage', ''),
                            medicine.get('contraindication', ''),
                            medicine.get('notes', ''),
                            existing[0]
                        ))

                        self.db.execute('''
                            UPDATE inventory 
                            SET quantity=?, unit=?, price=?, min_stock=?, notes=?
                            WHERE medicine_id=?
                        ''', (
                            medicine.get('quantity', 0),
                            medicine.get('unit', 'g'),
                            medicine.get('price', 0),
                            medicine.get('min_stock', 10),
                            medicine.get('notes', ''),
                            existing[0]
                        ))
                        updated += 1
                    else:
                        self.db.execute('''
                            INSERT INTO medicines 
                            (name, alias, category, nature, taste, meridian, 
                             efficacy, indications, usage, dosage, contraindication, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            medicine['name'],
                            medicine.get('alias', ''),
                            medicine.get('category', ''),
                            medicine.get('nature', ''),
                            medicine.get('taste', ''),
                            medicine.get('meridian', ''),
                            medicine.get('efficacy', ''),
                            medicine.get('indications', ''),
                            medicine.get('usage', ''),
                            medicine.get('dosage', ''),
                            medicine.get('contraindication', ''),
                            medicine.get('notes', '')
                        ))

                        med_id = self.db.fetchone(
                            "SELECT id FROM medicines WHERE name = ?",
                            (medicine['name'],)
                        )[0]

                        self.db.execute('''
                            INSERT INTO inventory 
                            (medicine_id, quantity, unit, price, min_stock, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            med_id,
                            medicine.get('quantity', 0),
                            medicine.get('unit', 'g'),
                            medicine.get('price', 0),
                            medicine.get('min_stock', 10),
                            medicine.get('notes', '')
                        ))
                        added += 1

                    self.progress.emit(int((i + 1) / total * 100))

                except Exception as e:
                    print(f"导入 {medicine['name']} 时出错: {e}")
                    continue

            self.finished.emit(True, f"导入完成！新增 {added} 味，更新 {updated} 味", added, updated)

        except Exception as e:
            self.finished.emit(False, f"导入失败: {str(e)}", 0, 0)


class ImportDialog(QDialog):
    """
    Windows 7优化版导入对话框
    白底黑字风格
    """

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle('批量导入药材')
        self.setModal(True)
        self.setFixedWidth(480)
        self.setStyleSheet("background-color: #ffffff;")
        self.init_ui()

    def _get_font(self, size, bold=False):
        font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
        font_db = QFontDatabase()
        if "Microsoft YaHei" not in font_db.families():
            font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
        return font

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        title_label = QLabel('数据导入向导')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self._get_font(16, bold=True))
        title_label.setStyleSheet('color: #000000; margin-bottom: 5px;')

        info_label = QLabel('即将把常用中药材基础数据同步到本地数据库。\n此过程可能需要几分钟，请勿关闭程序。')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(
            'color: #333333; padding: 12px; background-color: #f5f5f5; border-radius: 4px; border: 1px solid #e0e0e0;')
        info_label.setFont(self._get_font(10))

        progress_card = QFrame()
        progress_card.setStyleSheet('background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px;')
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        progress_layout.setSpacing(12)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f5f5f5;
                border-radius: 4px;
                text-align: center;
                border: 1px solid #e0e0e0;
                color: #000000;
                font-weight: bold;
                height: 22px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #000000;
                border-radius: 3px;
            }
        """)

        self.status_label = QLabel('准备就绪')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(self._get_font(9))
        self.status_label.setStyleSheet('color: #666666;')

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.start_btn = QPushButton('开始导入')
        self.start_btn.setFixedHeight(44)
        self.start_btn.setFont(self._get_font(11, bold=True))
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999999;
                border-color: #cccccc;
            }
        """)
        self.start_btn.clicked.connect(self.start_import)

        self.close_btn = QPushButton('关闭')
        self.close_btn.setFixedHeight(44)
        self.close_btn.setFont(self._get_font(11, bold=True))
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.close_btn)

        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addWidget(progress_card)
        layout.addLayout(btn_layout)

    def start_import(self):
        self.start_btn.setEnabled(False)
        self.start_btn.setText('导入中...')
        self.status_label.setText('正在连接数据库并校验数据...')
        self.status_label.setStyleSheet('color: #000000; font-weight: bold;')

        self.import_thread = ImportThread(self.db)
        self.import_thread.progress.connect(self.update_progress)
        self.import_thread.finished.connect(self.import_finished)
        self.import_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.status_label.setText(f'处理进度：{value}%')

    def import_finished(self, success, message, added, updated):
        self.status_label.setText(message)
        if success:
            self.status_label.setStyleSheet('color: #000000; font-weight: bold;')
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #f5f5f5;
                    border-radius: 4px;
                    text-align: center;
                    border: 1px solid #e0e0e0;
                    color: #000000;
                    font-weight: bold;
                    height: 22px;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #000000;
                    border-radius: 3px;
                }
            """)
            QMessageBox.information(self, '成功', message)
        else:
            self.status_label.setStyleSheet('color: #ff4d4f; font-weight: bold;')
            QMessageBox.warning(self, '提示', message)

        self.close_btn.setEnabled(True)
        self.start_btn.setEnabled(False)
        self.start_btn.setText('导入完成')
