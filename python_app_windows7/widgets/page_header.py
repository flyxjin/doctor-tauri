from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.responsive_font import get_font_manager


class PageHeader(QWidget):
    PAGE_CONFIG = {
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
        }
    }
    
    def __init__(self, page_key='medicine', parent=None):
        super().__init__(parent)
        self.font_manager = get_font_manager()
        self._page_key = page_key
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        self.indicator = QFrame()
        self.indicator.setObjectName('page_indicator')
        self.indicator.setFixedWidth(4)
        
        text_container = QWidget()
        text_container.setObjectName('header_text_container')
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        self.title_label = QLabel()
        self.title_label.setObjectName('header_title')
        
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName('header_subtitle')
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        
        main_layout.addWidget(self.indicator)
        main_layout.addWidget(text_container)
        main_layout.addStretch()
        
        self._apply_styles()
        self.set_page(self._page_key)
    
    def _apply_styles(self):
        base_size = self.font_manager.current_base_size
        title_size = int(base_size * 1.4)
        subtitle_size = int(base_size * 0.85)
        
        self.setStyleSheet(f'''
            PageHeader {{
                background-color: transparent;
                padding: 8px 0;
            }}
            QFrame#page_indicator {{
                background-color: #1890ff;
                border-radius: 2px;
            }}
            QWidget#header_text_container {{
                background-color: transparent;
            }}
            QLabel#header_title {{
                color: #262626;
                font-size: {title_size}px;
                font-weight: 500;
            }}
            QLabel#header_subtitle {{
                color: #8c8c8c;
                font-size: {subtitle_size}px;
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
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        self.indicator = QFrame()
        self.indicator.setObjectName('header_indicator')
        self.indicator.setFixedWidth(3)
        
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)
        
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
        title_size = int(base_size * 1.2)
        subtitle_size = int(base_size * 0.85)
        
        self.setStyleSheet(f'''
            QFrame#compact_header {{
                background-color: #fafafa;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
            }}
            QFrame#header_indicator {{
                background-color: #1890ff;
                border-radius: 1px;
            }}
            QLabel#compact_title {{
                color: #262626;
                font-size: {title_size}px;
                font-weight: 500;
            }}
            QLabel#compact_subtitle {{
                color: #8c8c8c;
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
