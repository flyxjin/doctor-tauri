# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.theme import AppColors
from utils.responsive_font import get_font_manager


class PageHeader(QWidget):
    PAGE_CONFIG = {
        'dashboard': {
            'title': '首页概览',
            'subtitle': '经营数据一览'
        },
        'medicine': {
            'title': '药材管理',
            'subtitle': '中药材信息管理与查询'
        },
        'prescription': {
            'title': '开处方',
            'subtitle': '中医处方开具与管理'
        },
        'patient': {
            'title': '客户管理',
            'subtitle': '患者档案管理与历史处方查询'
        },
        'inventory': {
            'title': '库存管理',
            'subtitle': '药材库存监控与调配'
        },
        'history': {
            'title': '处方历史',
            'subtitle': '历史处方查询与统计'
        },
        'statistics': {
            'title': '销售统计',
            'subtitle': '营收汇总与数据分析'
        }
    }

    def __init__(self, page_key='medicine', parent=None):
        super().__init__(parent)
        self.font_manager = get_font_manager()
        self._page_key = page_key
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 16)
        main_layout.setSpacing(0)

        text_container = QWidget()
        text_container.setObjectName('header_text_container')
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        self.title_label = QLabel()
        self.title_label.setObjectName('header_title')
        self.title_label.setMinimumHeight(28)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName('header_subtitle')
        self.subtitle_label.setMinimumHeight(18)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        main_layout.addWidget(text_container)
        main_layout.addStretch()

        self._apply_styles()
        self.set_page(self._page_key)

    def _apply_styles(self):
        base_size = self.font_manager.current_base_size
        title_size = int(base_size * 1.6)
        subtitle_size = int(base_size * 0.85)

        self.setStyleSheet(f'''
            PageHeader {{
                background-color: transparent;
                padding: 0;
            }}
            QWidget#header_text_container {{
                background-color: transparent;
            }}
            QLabel#header_title {{
                color: {AppColors.TEXT_HEADING};
                font-size: {title_size}px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            QLabel#header_subtitle {{
                color: {AppColors.TEXT_MUTED};
                font-size: {subtitle_size}px;
                font-weight: 400;
            }}
        ''')

    def set_page(self, page_key):
        config = self.PAGE_CONFIG.get(page_key, self.PAGE_CONFIG['medicine'])

        self.title_label.setText(config.get('title', '页面标题'))
        self.subtitle_label.setText(config.get('subtitle', ''))
        self._page_key = page_key

    def update_fonts(self):
        self._apply_styles()

    def get_current_page(self):
        return self._page_key


class CompactHeader(QFrame):
    def __init__(self, title='', subtitle='', parent=None):
        super().__init__(parent)
        self.font_manager = get_font_manager()
        self._title = title
        self._subtitle = subtitle
        self.init_ui()

    def init_ui(self):
        self.setObjectName('compact_header')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.indicator = QFrame()
        self.indicator.setObjectName('header_indicator')
        self.indicator.setFixedWidth(3)

        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        self.title_label = QLabel(self._title)
        self.title_label.setObjectName('compact_title')

        self.subtitle_label = QLabel(self._subtitle)
        self.subtitle_label.setObjectName('compact_subtitle')

        text_layout.addWidget(self.title_label)
        if self._subtitle:
            text_layout.addWidget(self.subtitle_label)

        layout.addWidget(self.indicator)
        layout.addWidget(text_container)
        layout.addStretch()

        self._apply_styles()

    def _apply_styles(self):
        base_size = self.font_manager.current_base_size
        title_size = int(base_size * 1.1)
        subtitle_size = int(base_size * 0.8)

        self.setStyleSheet(f'''
            QFrame#compact_header {{
                background-color: {AppColors.BG_CARD};
                border: 1px solid {AppColors.BORDER};
                border-radius: {AppColors.RADIUS_MD};
            }}
            QFrame#header_indicator {{
                background-color: {AppColors.ACCENT};
                border-radius: 1px;
            }}
            QLabel#compact_title {{
                color: {AppColors.TEXT_HEADING};
                font-size: {title_size}px;
                font-weight: 600;
            }}
            QLabel#compact_subtitle {{
                color: {AppColors.TEXT_MUTED};
                font-size: {subtitle_size}px;
            }}
        ''')

    def set_title(self, title, subtitle=''):
        self._title = title
        self._subtitle = subtitle
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))

    def update_fonts(self):
        self._apply_styles()
