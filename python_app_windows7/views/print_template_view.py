# -*- coding: utf-8 -*-
"""
打印模板定制视图 - Windows 7兼容版本
支持自定义处方打印格式
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QComboBox, QGroupBox,
                             QSpinBox, QCheckBox, QDialog, QMessageBox,
                             QColorDialog, QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import logging

logger = logging.getLogger('MedicineSystem')


class PrintTemplateManager:
    """打印模板管理器"""
    
    DEFAULT_TEMPLATES = {
        'standard': {
            'name': '标准模板',
            'page_width': 80,
            'page_height': 0,
            'font_family': 'SimSun',
            'font_size': 10,
            'title_font_size': 14,
            'show_logo': True,
            'show_border': True,
            'header_template': '''
<div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px;">
    <h2 style="margin: 5px 0;">中药材处方单</h2>
    <p style="margin: 5px 0; font-size: 12px;">专业中医药服务</p>
</div>
''',
            'body_template': '''
<div style="padding: 15px 0;">
    <table style="width: 100%; margin-bottom: 10px;">
        <tr>
            <td style="width: 50%;">患者姓名：{patient_name}</td>
            <td style="width: 25%;">年龄：{patient_age}岁</td>
            <td style="width: 25%;">性别：{patient_gender}</td>
        </tr>
    </table>
    <p style="margin: 8px 0;">诊断：{diagnosis}</p>
    <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th style="border: 1px solid #000; padding: 8px; text-align: left;">药材名称</th>
                <th style="border: 1px solid #000; padding: 8px; text-align: center; width: 80px;">数量</th>
                <th style="border: 1px solid #000; padding: 8px; text-align: right; width: 80px;">单价</th>
                <th style="border: 1px solid #000; padding: 8px; text-align: right; width: 80px;">金额</th>
            </tr>
        </thead>
        <tbody>
            {items}
        </tbody>
    </table>
</div>
''',
            'footer_template': '''
<div style="border-top: 1px solid #000; padding-top: 10px; margin-top: 10px;">
    <table style="width: 100%;">
        <tr>
            <td style="width: 50%;"><b>总计：¥{total_amount}</b></td>
            <td style="width: 50%; text-align: right;">日期：{date}</td>
        </tr>
    </table>
    <p style="margin-top: 15px; font-size: 11px; color: #666;">
        温馨提示：请遵医嘱服药，如有不适请及时就医。
    </p>
</div>
'''
        },
        'simple': {
            'name': '简洁模板',
            'page_width': 80,
            'page_height': 0,
            'font_family': 'SimSun',
            'font_size': 10,
            'title_font_size': 12,
            'show_logo': False,
            'show_border': False,
            'header_template': '''
<div style="text-align: center;">
    <h3 style="margin: 5px 0;">处方笺</h3>
</div>
''',
            'body_template': '''
<div style="padding: 10px 0;">
    <p>患者：{patient_name}  年龄：{patient_age}  性别：{patient_gender}</p>
    <p>诊断：{diagnosis}</p>
    <hr>
    <p><b>处方：</b></p>
    <p>{simple_items}</p>
</div>
''',
            'footer_template': '''
<div style="margin-top: 15px;">
    <p>合计：¥{total_amount}  日期：{date}</p>
</div>
'''
        },
        'detailed': {
            'name': '详细模板',
            'page_width': 210,
            'page_height': 297,
            'font_family': 'SimSun',
            'font_size': 11,
            'title_font_size': 16,
            'show_logo': True,
            'show_border': True,
            'header_template': '''
<div style="text-align: center; border: 2px solid #000; padding: 15px; margin-bottom: 15px;">
    <h2 style="margin: 0 0 10px 0;">中药材处方单</h2>
    <p style="margin: 0; font-size: 12px;">详细版</p>
</div>
''',
            'body_template': '''
<div style="padding: 10px;">
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
        <tr>
            <td style="border: 1px solid #000; padding: 8px; width: 25%;">患者姓名</td>
            <td style="border: 1px solid #000; padding: 8px; width: 25%;">{patient_name}</td>
            <td style="border: 1px solid #000; padding: 8px; width: 25%;">年龄</td>
            <td style="border: 1px solid #000; padding: 8px; width: 25%;">{patient_age}岁</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; padding: 8px;">性别</td>
            <td style="border: 1px solid #000; padding: 8px;">{patient_gender}</td>
            <td style="border: 1px solid #000; padding: 8px;">开具日期</td>
            <td style="border: 1px solid #000; padding: 8px;">{date}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #000; padding: 8px;">诊断</td>
            <td colspan="3" style="border: 1px solid #000; padding: 8px;">{diagnosis}</td>
        </tr>
    </table>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f5f5f5;">
                <th style="border: 1px solid #000; padding: 10px;">序号</th>
                <th style="border: 1px solid #000; padding: 10px;">药材名称</th>
                <th style="border: 1px solid #000; padding: 10px;">数量</th>
                <th style="border: 1px solid #000; padding: 10px;">单价</th>
                <th style="border: 1px solid #000; padding: 10px;">金额</th>
            </tr>
        </thead>
        <tbody>
            {items}
        </tbody>
        <tfoot>
            <tr>
                <td colspan="4" style="border: 1px solid #000; padding: 10px; text-align: right;"><b>合计：</b></td>
                <td style="border: 1px solid #000; padding: 10px;"><b>¥{total_amount}</b></td>
            </tr>
        </tfoot>
    </table>
</div>
''',
            'footer_template': '''
<div style="margin-top: 20px; padding-top: 10px; border-top: 1px dashed #000;">
    <p style="font-size: 11px; color: #666;">
        <b>服药须知：</b><br>
        1. 请遵医嘱按时服药<br>
        2. 服药期间忌食生冷、辛辣食物<br>
        3. 如有不适请及时就医
    </p>
    <p style="text-align: right; margin-top: 20px;">
        医生签名：______________ &nbsp;&nbsp;&nbsp;&nbsp; 取药人签名：______________
    </p>
</div>
'''
        }
    }
    
    @classmethod
    def get_template(cls, template_id: str) -> dict:
        return cls.DEFAULT_TEMPLATES.get(template_id, cls.DEFAULT_TEMPLATES['standard'])
    
    @classmethod
    def get_template_list(cls) -> list:
        return [
            {'id': 'standard', 'name': '标准模板'},
            {'id': 'simple', 'name': '简洁模板'},
            {'id': 'detailed', 'name': '详细模板'}
        ]
    
    @classmethod
    def render_prescription(cls, template_id: str, prescription_data: dict) -> str:
        template = cls.get_template(template_id)
        
        items_html = ''
        simple_items = ''
        for i, item in enumerate(prescription_data.get('items', [])):
            items_html += f'''
            <tr>
                <td style="border: 1px solid #000; padding: 8px; text-align: center;">{i + 1}</td>
                <td style="border: 1px solid #000; padding: 8px;">{item['name']}</td>
                <td style="border: 1px solid #000; padding: 8px; text-align: center;">{item['quantity']}g</td>
                <td style="border: 1px solid #000; padding: 8px; text-align: right;">¥{item['price']}</td>
                <td style="border: 1px solid #000; padding: 8px; text-align: right;">¥{item['amount']:.2f}</td>
            </tr>
            '''
            simple_items += f"{item['name']} {item['quantity']}g  "
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: {template['font_family']};
            font-size: {template['font_size']}px;
            margin: 10px;
            padding: 0;
        }}
        h2, h3 {{
            font-family: {template['font_family']};
        }}
        table {{
            font-family: {template['font_family']};
            font-size: {template['font_size']}px;
        }}
    </style>
</head>
<body>
    {template['header_template']}
    {template['body_template'].format(
        patient_name=prescription_data.get('patient_name', ''),
        patient_age=prescription_data.get('patient_age', ''),
        patient_gender=prescription_data.get('patient_gender', ''),
        diagnosis=prescription_data.get('diagnosis', ''),
        items=items_html,
        simple_items=simple_items,
        total_amount=f"{prescription_data.get('total_amount', 0):.2f}",
        date=prescription_data.get('date', '')
    )}
    {template['footer_template'].format(
        total_amount=f"{prescription_data.get('total_amount', 0):.2f}",
        date=prescription_data.get('date', '')
    )}
</body>
</html>
'''
        return html


class PrintTemplateView(QWidget):
    """打印模板定制视图"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self._current_template_id = 'standard'
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title_label = QLabel('打印模板定制')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold; color: #000000;')
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        template_group = QGroupBox('模板选择')
        template_layout = QHBoxLayout(template_group)
        
        template_layout.addWidget(QLabel('选择模板:'))
        
        self.template_combo = QComboBox()
        for t in PrintTemplateManager.get_template_list():
            self.template_combo.addItem(t['name'], t['id'])
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        
        layout.addWidget(template_group)
        
        preview_group = QGroupBox('模板预览')
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(300)
        
        preview_layout.addWidget(self.preview_text)
        layout.addWidget(preview_group)
        
        btn_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton('打印预览')
        self.preview_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 2px solid #000000; padding: 8px 24px;')
        self.preview_btn.clicked.connect(self.show_preview)
        
        self.print_test_btn = QPushButton('打印测试页')
        self.print_test_btn.setStyleSheet('background-color: #ffffff; color: #000000; border: 1px solid #000000; padding: 8px 24px;')
        self.print_test_btn.clicked.connect(self.print_test)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.print_test_btn)
        
        layout.addLayout(btn_layout)
        
        self._update_preview()
    
    def _on_template_changed(self):
        self._current_template_id = self.template_combo.currentData()
        self._update_preview()
    
    def _update_preview(self):
        test_data = {
            'patient_name': '张三',
            'patient_age': '45',
            'patient_gender': '男',
            'diagnosis': '感冒风寒证',
            'items': [
                {'name': '麻黄', 'quantity': 10, 'price': 0.5, 'amount': 5.0},
                {'name': '桂枝', 'quantity': 10, 'price': 0.3, 'amount': 3.0},
                {'name': '杏仁', 'quantity': 10, 'price': 0.4, 'amount': 4.0},
                {'name': '甘草', 'quantity': 6, 'price': 0.2, 'amount': 1.2},
            ],
            'total_amount': 13.2,
            'date': '2026-02-28'
        }
        
        html = PrintTemplateManager.render_prescription(self._current_template_id, test_data)
        self.preview_text.setHtml(html)
    
    def show_preview(self):
        from PyQt5.QtGui import QTextDocument
        from PyQt5.QtPrintSupport import QPrintPreviewDialog
        
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self._print_document)
        preview.exec_()
    
    def _print_document(self, printer):
        from PyQt5.QtGui import QTextDocument
        
        doc = QTextDocument()
        doc.setHtml(self.preview_text.toHtml())
        doc.print_(printer)
    
    def print_test(self):
        from PyQt5.QtPrintSupport import QPrintDialog
        from PyQt5.QtGui import QTextDocument
        
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.preview_text.toHtml())
            doc.print_(printer)
            QMessageBox.information(self, '成功', '打印任务已发送')
    
    def get_current_template_id(self) -> str:
        return self._current_template_id
