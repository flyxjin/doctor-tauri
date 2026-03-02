# -*- coding: utf-8 -*-
"""
批量导入对话框 - Fluent Design风格
支持Excel和CSV文件导入，完整的数据预览和校验功能
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QProgressBar, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QStackedWidget, QWidget, QFileDialog, QTextEdit,
                             QGraphicsDropShadowEffect, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QFontDatabase, QIcon
import csv
import os
import logging
from typing import List, Dict, Any, Optional

from utils.fluent_style import FluentColors, FluentTypography, FluentSpacing, FluentEffects

logger = logging.getLogger('MedicineSystem')

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class FluentButton(QPushButton):
    """Fluent Design风格按钮组件"""
    
    def __init__(self, text: str, variant: str = 'default', parent=None):
        super().__init__(text, parent)
        self._variant = variant
        self._apply_style()
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)
    
    def _apply_style(self):
        c = FluentColors
        e = FluentEffects
        t = FluentTypography
        s = FluentSpacing
        
        if self._variant == 'primary':
            self.setStyleSheet(f'''
                QPushButton {{
                    background-color: {c.BRAND['primary']};
                    color: {c.TEXT['inverted']};
                    border: none;
                    border-radius: {e.CORNERS['medium']}px;
                    padding: {s.SM}px {s.LG}px;
                    font-size: {t.SIZES['body']}px;
                    font-weight: {t.WEIGHTS['semibold']};
                    font-family: {t.FONT_FAMILY};
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {c.BRAND['primary_dark']};
                }}
                QPushButton:pressed {{
                    background-color: {c.BRAND['primary_darker']};
                }}
                QPushButton:disabled {{
                    background-color: {c.NEUTRAL['gray_100']};
                    color: {c.TEXT['disabled']};
                }}
            ''')
        elif self._variant == 'danger':
            self.setStyleSheet(f'''
                QPushButton {{
                    background-color: {c.SEMANTIC['error']};
                    color: {c.TEXT['inverted']};
                    border: none;
                    border-radius: {e.CORNERS['medium']}px;
                    padding: {s.SM}px {s.LG}px;
                    font-size: {t.SIZES['body']}px;
                    font-weight: {t.WEIGHTS['semibold']};
                    font-family: {t.FONT_FAMILY};
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {c.ACCENT['red_dark']};
                }}
                QPushButton:pressed {{
                    background-color: #8B1C1E;
                }}
                QPushButton:disabled {{
                    background-color: {c.NEUTRAL['gray_100']};
                    color: {c.TEXT['disabled']};
                }}
            ''')
        else:
            self.setStyleSheet(f'''
                QPushButton {{
                    background-color: {c.SURFACE['card']};
                    color: {c.TEXT['primary']};
                    border: 1px solid {c.STROKE['control']};
                    border-radius: {e.CORNERS['medium']}px;
                    padding: {s.SM}px {s.LG}px;
                    font-size: {t.SIZES['body']}px;
                    font-weight: {t.WEIGHTS['regular']};
                    font-family: {t.FONT_FAMILY};
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {c.SURFACE['card_hover']};
                    border-color: {c.STROKE['control_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {c.SURFACE['card_active']};
                    border-color: {c.STROKE['control_active']};
                    color: {c.TEXT['primary']};
                }}
                QPushButton:disabled {{
                    background-color: {c.SURFACE['background_tertiary']};
                    color: {c.TEXT['disabled']};
                    border-color: {c.STROKE['control_disabled']};
                }}
            ''')


class ImportWorker(QThread):
    """导入工作线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(int, int, int, list)
    
    def __init__(self, db, data_list: List[Dict]):
        super().__init__()
        self.db = db
        self.data_list = data_list
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        added = 0
        updated = 0
        errors = []
        total = len(self.data_list)
        
        for i, data in enumerate(self.data_list):
            if self._is_cancelled:
                errors.append("用户取消导入")
                break
                
            try:
                name = str(data.get('name', '')).strip()
                if not name:
                    errors.append(f"第{i+1}行: 药材名称不能为空")
                    continue
                
                existing = self.db.fetchone(
                    "SELECT id FROM medicines WHERE name = ?", (name,)
                )
                
                if existing:
                    existing_id = existing['id'] if isinstance(existing, dict) else existing[0]
                    self._update_medicine(existing_id, data)
                    self._update_inventory(existing_id, data)
                    updated += 1
                else:
                    med_id = self._insert_medicine(data)
                    self._insert_inventory(med_id, data)
                    added += 1
                    
            except Exception as e:
                errors.append(f"第{i+1}行({name}): {str(e)}")
                logger.error(f"导入数据失败: {e}")
                
            self.progress.emit(int((i + 1) / total * 100), f"正在处理: {name}")
            
        self.finished.emit(added, updated, len(errors), errors)
        
    def _update_medicine(self, med_id: int, data: Dict):
        self.db.execute('''
            UPDATE medicines 
            SET alias=?, category=?, nature=?, taste=?, meridian=?,
                efficacy=?, indications=?, usage=?, dosage=?, 
                contraindication=?, notes=?
            WHERE id=?
        ''', (
            data.get('alias', ''),
            data.get('category', ''),
            data.get('nature', ''),
            data.get('taste', ''),
            data.get('meridian', ''),
            data.get('efficacy', ''),
            data.get('indications', ''),
            data.get('usage', ''),
            data.get('dosage', ''),
            data.get('contraindication', ''),
            data.get('notes', ''),
            med_id
        ))
        
    def _update_inventory(self, med_id: int, data: Dict):
        if data.get('quantity') is not None:
            self.db.execute('''
                UPDATE inventory 
                SET quantity=?, unit=?, price=?, min_stock=?
                WHERE medicine_id=?
            ''', (
                float(data.get('quantity', 0) or 0),
                data.get('unit', 'g'),
                float(data.get('price', 0) or 0),
                float(data.get('min_stock', 10) or 10),
                med_id
            ))
            
    def _insert_medicine(self, data: Dict) -> int:
        self.db.execute('''
            INSERT INTO medicines 
            (name, alias, category, nature, taste, meridian, 
             efficacy, indications, usage, dosage, contraindication, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('alias', ''),
            data.get('category', ''),
            data.get('nature', ''),
            data.get('taste', ''),
            data.get('meridian', ''),
            data.get('efficacy', ''),
            data.get('indications', ''),
            data.get('usage', ''),
            data.get('dosage', ''),
            data.get('contraindication', ''),
            data.get('notes', '')
        ))
        result = self.db.fetchone("SELECT id FROM medicines WHERE name = ?", (data['name'],))
        return result['id'] if isinstance(result, dict) else result[0]
        
    def _insert_inventory(self, med_id: int, data: Dict):
        self.db.execute('''
            INSERT INTO inventory 
            (medicine_id, quantity, unit, price, min_stock, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            med_id,
            float(data.get('quantity', 0) or 0),
            data.get('unit', 'g'),
            float(data.get('price', 0) or 0),
            float(data.get('min_stock', 10) or 10),
            data.get('notes', '')
        ))


class DataValidator:
    """数据验证器"""
    
    VALID_NATURES = ['寒', '热', '温', '凉', '平', '微温', '微寒', '大热', '大寒', '']
    
    @classmethod
    def validate_row(cls, row_data: Dict, row_num: int) -> List[str]:
        errors = []
        
        name = str(row_data.get('name', '')).strip()
        if not name:
            errors.append(f"第{row_num}行: 药材名称不能为空")
        elif len(name) > 50:
            errors.append(f"第{row_num}行: 药材名称过长（最多50字符）")
            
        nature = str(row_data.get('nature', '')).strip()
        if nature and nature not in cls.VALID_NATURES:
            errors.append(f"第{row_num}行: 药性'{nature}'无效")
            
        for field in ['quantity', 'price', 'min_stock']:
            value = row_data.get(field)
            if value is not None and value != '':
                try:
                    v = float(value)
                    if v < 0:
                        errors.append(f"第{row_num}行: {field}不能为负数")
                except (ValueError, TypeError):
                    errors.append(f"第{row_num}行: {field}'{value}'不是有效数字")
                    
        return errors
    
    @classmethod
    def validate_all(cls, data_list: List[Dict]) -> tuple:
        all_errors = []
        valid_data = []
        
        for i, row_data in enumerate(data_list, 1):
            errors = cls.validate_row(row_data, i)
            if errors:
                all_errors.extend(errors)
            valid_data.append(row_data)
            
        return valid_data, all_errors


class FileDropArea(QFrame):
    """文件拖放区域"""
    
    file_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._init_ui()
        
    def _init_ui(self):
        c = FluentColors
        e = FluentEffects
        t = FluentTypography
        s = FluentSpacing
        
        self.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['background_tertiary']};
                border: 2px dashed {c.STROKE['control']};
                border-radius: {e.CORNERS['large']}px;
            }}
        ''')
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(s.SM)
        
        self.title_label = QLabel('拖放文件到此处')
        self.title_label.setStyleSheet(f'''
            font-size: {t.SIZES['body_large']}px;
            font-weight: {t.WEIGHTS['semibold']};
            color: {c.TEXT['primary']};
            font-family: {t.FONT_FAMILY};
        ''')
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.hint_label = QLabel('或点击下方按钮选择文件\n支持 .xlsx, .xls, .csv 格式')
        self.hint_label.setStyleSheet(f'''
            font-size: {t.SIZES['body_small']}px;
            color: {c.TEXT['tertiary']};
            font-family: {t.FONT_FAMILY};
        ''')
        self.hint_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)
        
        self.setMinimumHeight(180)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f'''
                QFrame {{
                    background-color: {c.BRAND['primary_lightest']};
                    border: 2px dashed {c.BRAND['primary']};
                    border-radius: {e.CORNERS['large']}px;
                }}
            ''')
            
    def dragLeaveEvent(self, event):
        c = FluentColors
        e = FluentEffects
        self.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['background_tertiary']};
                border: 2px dashed {c.STROKE['control']};
                border-radius: {e.CORNERS['large']}px;
            }}
        ''')
        
    def dropEvent(self, event):
        c = FluentColors
        e = FluentEffects
        self.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['background_tertiary']};
                border: 2px dashed {c.STROKE['control']};
                border-radius: {e.CORNERS['large']}px;
            }}
        ''')
        
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            self.file_dropped.emit(filepath)
            
    def set_file_loaded(self, filename: str):
        self.title_label.setText(f'{os.path.basename(filename)}')
        self.hint_label.setText('文件已加载，点击其他文件可重新选择')


class ImportDialog(QDialog):
    """
    Fluent Design风格批量导入对话框
    支持Excel/CSV文件导入，数据预览和校验
    """
    
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.worker = None
        self.preview_data = []
        self.validation_errors = []
        self.current_file = ''
        
        self._setup_window()
        self._init_ui()
        
    def _setup_window(self):
        self.setWindowTitle('批量导入药材数据')
        self.setModal(True)
        self.setMinimumSize(800, 650)
        self.resize(900, 700)
        
        c = FluentColors
        self.setStyleSheet(f'''
            QDialog {{
                background-color: {c.SURFACE['background_primary']};
            }}
        ''')
        
    def _get_font(self, size: int, bold: bool = False) -> QFont:
        font = QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal)
        font_db = QFontDatabase()
        if "Segoe UI" not in font_db.families():
            font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
            if "Microsoft YaHei" not in font_db.families():
                font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
        return font
        
    def _init_ui(self):
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(s.LG, s.LG, s.LG, s.LG)
        main_layout.setSpacing(s.MD)
        
        header_layout = QHBoxLayout()
        title_label = QLabel('批量导入药材数据')
        title_label.setFont(self._get_font(18, bold=True))
        title_label.setStyleSheet(f'color: {c.BRAND["primary"]};')
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        self.stacked_widget = QStackedWidget()
        
        self._create_select_page()
        self._create_preview_page()
        self._create_progress_page()
        self._create_result_page()
        
        main_layout.addWidget(self.stacked_widget)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(s.SM)
        
        self.back_btn = FluentButton('返回', 'default')
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setVisible(False)
        
        self.template_btn = FluentButton('下载模板', 'default')
        self.template_btn.clicked.connect(self._download_template)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.template_btn)
        
        self.next_btn = FluentButton('下一步', 'primary')
        self.next_btn.clicked.connect(self._go_next)
        self.next_btn.setEnabled(False)
        
        self.import_btn = FluentButton('开始导入', 'primary')
        self.import_btn.clicked.connect(self._start_import)
        self.import_btn.setVisible(False)
        
        self.cancel_import_btn = FluentButton('取消导入', 'danger')
        self.cancel_import_btn.clicked.connect(self._cancel_import)
        self.cancel_import_btn.setVisible(False)
        
        self.close_btn = FluentButton('关闭', 'default')
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setVisible(False)
        
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.cancel_import_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
    def _create_select_page(self):
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(s.LG)
        
        self.drop_area = FileDropArea()
        self.drop_area.file_dropped.connect(self._load_file)
        
        select_layout = QHBoxLayout()
        select_layout.setAlignment(Qt.AlignCenter)
        
        self.select_file_btn = FluentButton('选择文件', 'primary')
        self.select_file_btn.clicked.connect(self._select_file)
        
        hint_label = QLabel('支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式')
        hint_label.setStyleSheet(f'color: {c.TEXT["tertiary"]}; font-size: {t.SIZES["body_small"]}px;')
        
        select_layout.addWidget(self.select_file_btn)
        select_layout.addSpacing(s.LG)
        select_layout.addWidget(hint_label)
        
        layout.addWidget(self.drop_area)
        layout.addLayout(select_layout)
        
        help_frame = QFrame()
        help_frame.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SEMANTIC['info_background']};
                border: 1px solid {c.BRAND['primary_light']};
                border-radius: {e.CORNERS['medium']}px;
                padding: {s.MD}px;
            }}
        ''')
        help_layout = QVBoxLayout(help_frame)
        help_layout.setContentsMargins(s.MD, s.MD, s.MD, s.MD)
        
        help_title = QLabel('导入说明')
        help_title.setStyleSheet(f'font-weight: {t.WEIGHTS["semibold"]}; color: {c.BRAND["primary"]};')
        
        help_text = QLabel('''
• 必填字段：药材名称 (name)
• 可选字段：别名、分类、药性、药味、归经、功效、主治、用法、用量、禁忌、备注、库存数量、单位、单价、最低库存
• 重复的药材名称将更新已有数据
• CSV文件请使用UTF-8编码
        ''')
        help_text.setStyleSheet(f'color: {c.TEXT["secondary"]}; line-height: 1.6;')
        help_text.setWordWrap(True)
        
        help_layout.addWidget(help_title)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_frame)
        
        self.stacked_widget.addWidget(page)
        
    def _create_preview_page(self):
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(s.MD)
        
        info_frame = QFrame()
        info_frame.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['medium']}px;
            }}
        ''')
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(s.MD, s.SM, s.MD, s.SM)
        
        self.file_info_label = QLabel()
        self.file_info_label.setStyleSheet(f'font-weight: {t.WEIGHTS["semibold"]}; color: {c.TEXT["primary"]};')
        
        self.record_count_label = QLabel()
        self.record_count_label.setStyleSheet(f'color: {c.TEXT["secondary"]};')
        
        self.error_count_label = QLabel()
        
        info_layout.addWidget(self.file_info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.record_count_label)
        info_layout.addWidget(self.error_count_label)
        
        layout.addWidget(info_frame)
        
        preview_group = QFrame()
        preview_group.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['medium']}px;
            }}
        ''')
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(s.SM, s.SM, s.SM, s.SM)
        
        preview_title = QLabel('数据预览 (显示前20条)')
        preview_title.setStyleSheet(f'font-weight: {t.WEIGHTS["semibold"]}; color: {c.TEXT["primary"]}; margin-bottom: {s.SM}px;')
        preview_layout.addWidget(preview_title)
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setMinimumHeight(250)
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        error_group = QFrame()
        error_group.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SEMANTIC['error_background']};
                border: 1px solid {c.ACCENT['red_light']};
                border-radius: {e.CORNERS['medium']}px;
            }}
        ''')
        error_layout = QVBoxLayout(error_group)
        error_layout.setContentsMargins(s.SM, s.SM, s.SM, s.SM)
        
        error_title = QLabel('验证错误')
        error_title.setStyleSheet(f'font-weight: {t.WEIGHTS["semibold"]}; color: {c.SEMANTIC["error"]};')
        error_layout.addWidget(error_title)
        
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumHeight(100)
        self.error_text.setStyleSheet(f'''
            QTextEdit {{
                background-color: {c.SURFACE['card']};
                border: none;
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
            }}
        ''')
        error_layout.addWidget(self.error_text)
        
        self.error_group = error_group
        self.error_group.setVisible(False)
        
        layout.addWidget(self.error_group)
        
        self.stacked_widget.addWidget(page)
        
    def _create_progress_page(self):
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(s.XL)
        
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
            }}
        ''')
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(s.XXL, s.XXL, s.XXL, s.XXL)
        progress_layout.setSpacing(s.LG)
        progress_layout.setAlignment(Qt.AlignCenter)
        
        self.progress_title = QLabel('正在导入数据...')
        self.progress_title.setStyleSheet(f'''
            font-size: {t.SIZES['subtitle']}px;
            font-weight: {t.WEIGHTS['semibold']};
            color: {c.TEXT['primary']};
        ''')
        self.progress_title.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumWidth(400)
        self.progress_bar.setStyleSheet(f'''
            QProgressBar {{
                background-color: {c.NEUTRAL['gray_40']};
                border: none;
                border-radius: {e.CORNERS['circle']}px;
                text-align: center;
                height: 8px;
                color: transparent;
            }}
            QProgressBar::chunk {{
                background-color: {c.BRAND['primary']};
                border-radius: {e.CORNERS['circle']}px;
            }}
        ''')
        
        self.progress_status = QLabel('准备中...')
        self.progress_status.setStyleSheet(f'color: {c.TEXT["secondary"]}; font-size: {t.SIZES["body_small"]}px;')
        self.progress_status.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.progress_title)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_status)
        
        layout.addWidget(progress_frame)
        
        self.stacked_widget.addWidget(page)
        
    def _create_result_page(self):
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(s.XL)
        
        result_frame = QFrame()
        result_frame.setStyleSheet(f'''
            QFrame {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
            }}
        ''')
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(s.XXL, s.XXL, s.XXL, s.XXL)
        result_layout.setSpacing(s.LG)
        result_layout.setAlignment(Qt.AlignCenter)
        
        self.result_title = QLabel('导入完成')
        self.result_title.setStyleSheet(f'''
            font-size: {t.SIZES['subtitle']}px;
            font-weight: {t.WEIGHTS['semibold']};
            color: {c.TEXT['primary']};
        ''')
        self.result_title.setAlignment(Qt.AlignCenter)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(s.XXL)
        
        self.added_label = QLabel()
        self.added_label.setStyleSheet(f'''
            font-size: {t.SIZES['body_large']}px;
            color: {c.SEMANTIC['success']};
        ''')
        self.added_label.setAlignment(Qt.AlignCenter)
        
        self.updated_label = QLabel()
        self.updated_label.setStyleSheet(f'''
            font-size: {t.SIZES['body_large']}px;
            color: {c.BRAND['primary']};
        ''')
        self.updated_label.setAlignment(Qt.AlignCenter)
        
        self.error_result_label = QLabel()
        self.error_result_label.setStyleSheet(f'''
            font-size: {t.SIZES['body_large']}px;
            color: {c.SEMANTIC['error']};
        ''')
        self.error_result_label.setAlignment(Qt.AlignCenter)
        
        stats_layout.addStretch()
        stats_layout.addWidget(self.added_label)
        stats_layout.addWidget(self.updated_label)
        stats_layout.addWidget(self.error_result_label)
        stats_layout.addStretch()
        
        result_layout.addWidget(self.result_title)
        result_layout.addLayout(stats_layout)
        
        self.result_detail = QTextEdit()
        self.result_detail.setReadOnly(True)
        self.result_detail.setMaximumHeight(150)
        self.result_detail.setStyleSheet(f'''
            QTextEdit {{
                background-color: {c.SURFACE['background_tertiary']};
                border: none;
                border-radius: {e.CORNERS['medium']}px;
                padding: {s.SM}px;
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
            }}
        ''')
        result_layout.addWidget(self.result_detail)
        
        layout.addWidget(result_frame)
        
        self.stacked_widget.addWidget(page)
        
    def _select_file(self):
        file_filter = '数据文件 (*.xlsx *.xls *.csv);;Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv)'
        if not HAS_OPENPYXL:
            file_filter = 'CSV文件 (*.csv)'
            
        filename, _ = QFileDialog.getOpenFileName(self, '选择导入文件', '', file_filter)
        if filename:
            self._load_file(filename)
            
    def _load_file(self, filepath: str):
        c = FluentColors
        
        self.current_file = filepath
        self.drop_area.set_file_loaded(filepath)
        
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.csv':
                self.preview_data = self._parse_csv(filepath)
            elif ext in ['.xlsx', '.xls'] and HAS_OPENPYXL:
                self.preview_data = self._parse_excel(filepath)
            else:
                QMessageBox.warning(self, '错误', '不支持的文件格式')
                return
                
            if not self.preview_data:
                QMessageBox.warning(self, '错误', '文件中没有有效数据')
                return
                
            valid_data, errors = DataValidator.validate_all(self.preview_data)
            self.validation_errors = errors
            
            self._show_preview()
            
            self.next_btn.setEnabled(True)
            
        except Exception as e:
            logger.error(f"文件解析失败: {e}")
            QMessageBox.critical(self, '错误', f'文件解析失败:\n{str(e)}')
            
    def _parse_csv(self, filepath: str) -> List[Dict]:
        data = []
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    
                    if not headers or 'name' not in [h.lower() for h in headers]:
                        raise ValueError('文件必须包含name列（药材名称）')
                        
                    for row in reader:
                        normalized = {}
                        for key, value in row.items():
                            normalized[key.lower().strip()] = str(value).strip() if value else ''
                        if normalized.get('name'):
                            data.append(normalized)
                            
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise ValueError(f'CSV解析错误: {str(e)}')
                
        return data
        
    def _parse_excel(self, filepath: str) -> List[Dict]:
        data = []
        wb = openpyxl.load_workbook(filepath, read_only=True)
        ws = wb.active
        
        header_mapping = {
            'name': 'name',
            '药材名称': 'name',
            'alias': 'alias',
            '别名': 'alias',
            'category': 'category',
            '分类': 'category',
            'nature': 'nature',
            '药性': 'nature',
            'taste': 'taste',
            '药味': 'taste',
            'meridian': 'meridian',
            '归经': 'meridian',
            'efficacy': 'efficacy',
            '功效': 'efficacy',
            'indications': 'indications',
            '主治': 'indications',
            'usage': 'usage',
            '用法': 'usage',
            'dosage': 'dosage',
            '用量': 'dosage',
            'contraindication': 'contraindication',
            '禁忌': 'contraindication',
            'notes': 'notes',
            '备注': 'notes',
            'quantity': 'quantity',
            '库存数量': 'quantity',
            'unit': 'unit',
            '单位': 'unit',
            'price': 'price',
            '单价': 'price',
            'min_stock': 'min_stock',
            '最低库存': 'min_stock',
        }
        
        headers = []
        normalized_headers = []
        for cell in ws[1]:
            if cell.value:
                raw_header = str(cell.value).strip()
                headers.append(raw_header)
                normalized = header_mapping.get(raw_header.lower(), raw_header.lower())
                normalized_headers.append(normalized)
            else:
                headers.append('')
                normalized_headers.append('')
                
        if 'name' not in normalized_headers:
            wb.close()
            raise ValueError('Excel文件必须包含name列（药材名称）')
            
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not any(row):
                continue
            item = {}
            for i, norm_header in enumerate(normalized_headers):
                if norm_header and i < len(row):
                    value = row[i]
                    if value is not None:
                        item[norm_header] = str(value).strip() if isinstance(value, str) else value
                    else:
                        item[norm_header] = ''
            if item.get('name'):
                data.append(item)
                
        wb.close()
        return data
        
    def _show_preview(self):
        c = FluentColors
        t = FluentTypography
        
        self.file_info_label.setText(f'{os.path.basename(self.current_file)}')
        self.record_count_label.setText(f'共 {len(self.preview_data)} 条数据')
        
        if self.validation_errors:
            self.error_count_label.setText(f' | {len(self.validation_errors)} 个警告')
            self.error_count_label.setStyleSheet(f'color: {c.ACCENT["orange"]}; font-weight: {t.WEIGHTS["semibold"]};')
            self.error_group.setVisible(True)
            self.error_text.clear()
            for err in self.validation_errors[:20]:
                self.error_text.append(f'• {err}')
            if len(self.validation_errors) > 20:
                self.error_text.append(f'... 还有 {len(self.validation_errors) - 20} 个警告')
        else:
            self.error_count_label.setText(' | 数据验证通过')
            self.error_count_label.setStyleSheet(f'color: {c.SEMANTIC["success"]}; font-weight: {t.WEIGHTS["semibold"]};')
            self.error_group.setVisible(False)
            
        self.preview_table.clear()
        if self.preview_data:
            headers = list(self.preview_data[0].keys())
            display_headers = [h for h in headers if h in ['name', 'alias', 'category', 'nature', 'taste', 'quantity', 'price']]
            
            self.preview_table.setColumnCount(len(display_headers))
            self.preview_table.setHorizontalHeaderLabels(display_headers)
            self.preview_table.setRowCount(min(20, len(self.preview_data)))
            
            for row_idx, row_data in enumerate(self.preview_data[:20]):
                for col_idx, header in enumerate(display_headers):
                    value = row_data.get(header, '')
                    item = QTableWidgetItem(str(value)[:30] if value else '')
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.preview_table.setItem(row_idx, col_idx, item)
                    
            self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
    def _go_next(self):
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 0:
            self.stacked_widget.setCurrentIndex(1)
            self.next_btn.setVisible(False)
            self.import_btn.setVisible(True)
            self.back_btn.setVisible(True)
            self.template_btn.setVisible(False)
            
    def _go_back(self):
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 1:
            self.stacked_widget.setCurrentIndex(0)
            self.next_btn.setVisible(True)
            self.next_btn.setEnabled(True)
            self.import_btn.setVisible(False)
            self.back_btn.setVisible(False)
            self.template_btn.setVisible(True)
        elif current_index == 3:
            self.stacked_widget.setCurrentIndex(0)
            self.back_btn.setVisible(False)
            self.close_btn.setVisible(False)
            self.template_btn.setVisible(True)
            self.next_btn.setVisible(True)
            self.next_btn.setEnabled(False)
            
    def _start_import(self):
        if not self.preview_data:
            return
            
        reply = QMessageBox.question(
            self, '确认导入',
            f'确定要导入 {len(self.preview_data)} 条数据吗？\n重复的药材名称将更新已有数据。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        self.import_btn.setVisible(False)
        self.back_btn.setVisible(False)
        self.cancel_import_btn.setVisible(True)
        self.stacked_widget.setCurrentIndex(2)
        
        self.worker = ImportWorker(self.db, self.preview_data)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()
        
    def _cancel_import(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.progress_title.setText('正在取消...')
            
    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.progress_status.setText(message)
        
    def _on_finished(self, added: int, updated: int, error_count: int, errors: List[str]):
        c = FluentColors
        t = FluentTypography
        
        self.cancel_import_btn.setVisible(False)
        self.stacked_widget.setCurrentIndex(3)
        
        if error_count > 0 and not any('取消' in e for e in errors):
            self.result_title.setText('导入完成（有错误）')
        elif any('取消' in e for e in errors):
            self.result_title.setText('导入已取消')
        else:
            self.result_title.setText('导入完成')
            
        self.added_label.setText(f'新增: {added} 条')
        self.updated_label.setText(f'更新: {updated} 条')
        self.error_result_label.setText(f'错误: {error_count} 条')
        
        self.result_detail.clear()
        self.result_detail.append(f'导入时间: {self._get_current_time()}')
        self.result_detail.append(f'文件: {os.path.basename(self.current_file)}')
        self.result_detail.append('')
        
        if errors:
            self.result_detail.append('错误详情:')
            for err in errors[:10]:
                self.result_detail.append(f'  • {err}')
            if len(errors) > 10:
                self.result_detail.append(f'  ... 还有 {len(errors) - 10} 条错误')
                
        logger.info(f"批量导入完成: 新增{added}条, 更新{updated}条, 错误{error_count}条")
        
        self.close_btn.setVisible(True)
        
    def _get_current_time(self) -> str:
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def _download_template(self):
        format_dialog = QMessageBox(self)
        format_dialog.setWindowTitle('选择模板格式')
        format_dialog.setText('请选择要下载的模板格式:')
        format_dialog.setStyleSheet(f'''
            QMessageBox {{
                background-color: {FluentColors.SURFACE['card']};
            }}
        ''')
        
        excel_btn = format_dialog.addButton('Excel格式 (.xlsx)', QMessageBox.AcceptRole)
        csv_btn = format_dialog.addButton('CSV格式 (.csv)', QMessageBox.RejectRole)
        format_dialog.addButton(QMessageBox.Cancel)
        
        format_dialog.exec_()
        
        clicked_text = format_dialog.clickedButton().text()
        
        if clicked_text == 'Excel格式 (.xlsx)' and HAS_OPENPYXL:
            filename, _ = QFileDialog.getSaveFileName(
                self, '保存Excel模板', '药材导入模板.xlsx', 'Excel文件 (*.xlsx)'
            )
            if filename:
                if self._generate_excel_template(filename):
                    QMessageBox.information(self, '成功', f'Excel模板已保存到:\n{filename}')
                else:
                    QMessageBox.warning(self, '失败', '生成Excel模板失败')
        elif clicked_text == 'CSV格式 (.csv)' or not HAS_OPENPYXL:
            filename, _ = QFileDialog.getSaveFileName(
                self, '保存CSV模板', '药材导入模板.csv', 'CSV文件 (*.csv)'
            )
            if filename:
                if self._generate_csv_template(filename):
                    QMessageBox.information(self, '成功', f'CSV模板已保存到:\n{filename}')
                else:
                    QMessageBox.warning(self, '失败', '生成CSV模板失败')
                    
    def _generate_excel_template(self, filepath: str) -> bool:
        if not HAS_OPENPYXL:
            return False
            
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = '药材导入模板'
            
            headers = [
                ('name', '药材名称 *必填*', True),
                ('alias', '别名', False),
                ('category', '分类', False),
                ('nature', '药性', False),
                ('taste', '药味', False),
                ('meridian', '归经', False),
                ('efficacy', '功效', False),
                ('indications', '主治', False),
                ('usage', '用法', False),
                ('dosage', '用量', False),
                ('contraindication', '禁忌', False),
                ('notes', '备注', False),
                ('quantity', '库存数量', False),
                ('unit', '单位', False),
                ('price', '单价', False),
                ('min_stock', '最低库存', False),
            ]
            
            required_fill = PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
            normal_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF', size=11)
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for col_idx, (name, label, required) in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.value = name
                cell.fill = required_fill if required else normal_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                ws.column_dimensions[get_column_letter(col_idx)].width = 15
                
                comment_cell = ws.cell(row=2, column=col_idx)
                comment_cell.value = label
                comment_cell.font = Font(italic=True, color='666666', size=10)
                comment_cell.alignment = Alignment(horizontal='center', vertical='center')
            
            sample_data = [
                ['人参', '黄参', '补虚药', '温', '甘、微苦', '归脾、肺、心经', '大补元气', '体虚欲脱', '煎服', '3-9g', '实证禁服', '', 500, 'g', 85.0, 50],
                ['黄芪', '黄耆', '补虚药', '微温', '甘', '归脾、肺经', '补气升阳', '气虚乏力', '煎服', '9-30g', '实证禁服', '', 600, 'g', 42.0, 60],
            ]
            
            for row_idx, row_data in enumerate(sample_data, 3):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.border = thin_border
                    
            wb.save(filepath)
            return True
            
        except Exception as e:
            logger.error(f"生成Excel模板失败: {e}")
            return False
            
    def _generate_csv_template(self, filepath: str) -> bool:
        try:
            headers = ['name', 'alias', 'category', 'nature', 'taste', 'meridian', 
                      'efficacy', 'indications', 'usage', 'dosage', 'contraindication', 
                      'notes', 'quantity', 'unit', 'price', 'min_stock']
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerow(['人参', '黄参', '补虚药', '温', '甘、微苦', '归脾、肺、心经', 
                               '大补元气', '体虚欲脱', '煎服', '3-9g', '实证禁服', '', 500, 'g', 85.0, 50])
                writer.writerow(['黄芪', '黄耆', '补虚药', '微温', '甘', '归脾、肺经', 
                               '补气升阳', '气虚乏力', '煎服', '9-30g', '实证禁服', '', 600, 'g', 42.0, 60])
            
            return True
            
        except Exception as e:
            logger.error(f"生成CSV模板失败: {e}")
            return False
            
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, '确认关闭',
                '导入正在进行中，确定要关闭吗？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            self.worker.cancel()
            self.worker.wait()
        event.accept()
