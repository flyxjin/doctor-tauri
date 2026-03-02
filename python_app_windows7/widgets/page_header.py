# -*- coding: utf-8 -*-
"""
页面头部导航 - 现代简约设计
清晰、易用、符合 WCAG 标准
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter

from utils.style import UIStyles


def get_font(size: int, bold: bool = False) -> QFont:
    """获取系统字体"""
    from PyQt5.QtGui import QFontDatabase
    font = QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal)
    font_db = QFontDatabase()
    if "Segoe UI" not in font_db.families():
        font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
        if "Microsoft YaHei" not in font_db.families():
            font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
    return font


class PageHeader(QWidget):
    """
    页面头部导航组件 - 现代设计
    
    设计规范:
    - 高度: 56px
    - 字号: 标题 18px, 副标题 12px
    - 对比度: ≥ 4.5:1
    """
    
    PAGE_CONFIG = {
        'dashboard': {
            'title': '数据统计',
            'subtitle': '销售统计与数据分析'
        },
        'medicine': {
            'title': '药材管理',
            'subtitle': '中药材信息管理与查询'
        },
        'prescription': {
            'title': '开处方',
            'subtitle': '中医处方开具与管理'
        },
        'inventory': {
            'title': '库存管理',
            'subtitle': '药材库存监控与调配'
        },
        'history': {
            'title': '处方历史',
            'subtitle': '历史处方查询与统计'
        },
        'template': {
            'title': '处方模板',
            'subtitle': '常用处方模板管理'
        },
        'patient': {
            'title': '患者管理',
            'subtitle': '患者信息与就诊记录'
        },
        'print': {
            'title': '打印设置',
            'subtitle': '打印模板与打印配置'
        }
    }
    
    def __init__(self, page_key='medicine', parent=None):
        super().__init__(parent)
        self._page_key = page_key
        self.setMinimumHeight(56)
        self.setMaximumHeight(64)
        self._init_ui()
    
    def _init_ui(self):
        c = UIStyles.COLORS
        dt = UIStyles.DT
        s = UIStyles.SPACING
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(s['4'], s['3'], s['4'], s['3'])
        main_layout.setSpacing(s['3'])
        
        self.indicator = QFrame()
        self.indicator.setFixedWidth(4)
        self.indicator.setStyleSheet(f'''
            QFrame {{
                background-color: {dt.COLORS['primary']['default']};
                border-radius: 2px;
            }}
        ''')
        
        text_container = QWidget()
        text_container.setStyleSheet('background: transparent;')
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet(f'''
            QLabel {{
                color: {c['text_main']};
                font-size: 18px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        ''')
        self.title_label.setFont(get_font(18, bold=True))
        
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet(f'''
            QLabel {{
                color: {c['text_muted']};
                font-size: 12px;
                background: transparent;
                border: none;
            }}
        ''')
        self.subtitle_label.setFont(get_font(12))
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        
        main_layout.addWidget(self.indicator)
        main_layout.addWidget(text_container)
        main_layout.addStretch()
        
        self.set_page(self._page_key)
    
    def set_page(self, page_key):
        config = self.PAGE_CONFIG.get(page_key, self.PAGE_CONFIG['medicine'])
        self.title_label.setText(config.get('title', '页面标题'))
        self.subtitle_label.setText(config.get('subtitle', ''))
        self._page_key = page_key
    
    def update_title(self, page_key):
        self.set_page(page_key)
    
    def update_fonts(self):
        pass
    
    def get_current_page(self):
        return self._page_key


class CompactHeader(QFrame):
    """紧凑型头部 - 用于子页面"""
    
    def __init__(self, title='', subtitle='', parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._init_ui()
    
    def _init_ui(self):
        c = UIStyles.COLORS
        dt = UIStyles.DT
        s = UIStyles.SPACING
        
        self.setMinimumHeight(48)
        self.setStyleSheet(f'''
            QFrame {{
                background-color: {dt.COLORS['neutral']['gray']['50']};
                border: 1px solid {c['border']};
                border-radius: 6px;
            }}
        ''')
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(s['3'], s['2'], s['3'], s['2'])
        layout.setSpacing(s['2'])
        
        self.indicator = QFrame()
        self.indicator.setFixedWidth(3)
        self.indicator.setStyleSheet(f'''
            QFrame {{
                background-color: {dt.COLORS['primary']['default']};
                border-radius: 1px;
            }}
        ''')
        
        text_container = QWidget()
        text_container.setStyleSheet('background: transparent;')
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        
        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f'''
            QLabel {{
                color: {c['text_main']};
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        ''')
        
        self.subtitle_label = QLabel(self._subtitle)
        self.subtitle_label.setStyleSheet(f'''
            QLabel {{
                color: {c['text_muted']};
                font-size: 11px;
                background: transparent;
                border: none;
            }}
        ''')
        
        text_layout.addWidget(self.title_label)
        if self._subtitle:
            text_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(self.indicator)
        layout.addWidget(text_container)
        layout.addStretch()
    
    def set_title(self, title, subtitle=''):
        self._title = title
        self._subtitle = subtitle
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))
    
    def update_fonts(self):
        pass
