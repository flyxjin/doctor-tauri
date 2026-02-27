# -*- coding: utf-8 -*-
"""
侧边栏组件 - Windows 7兼容版本
提供可复用的侧边栏导航组件
白底黑字风格
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QFontDatabase


class SidebarWidget(QWidget):
    """
    侧边栏导航组件 - 白底黑字风格
    
    信号:
        nav_clicked(str): 导航按钮点击时发出，参数为视图名称
        import_clicked: 导入按钮点击时发出
    """
    nav_clicked = pyqtSignal(str)
    import_clicked = pyqtSignal()
    
    NAV_ITEMS = [
        ('药材管理', 'medicine'),
        ('开处方', 'prescription'),
        ('库存管理', 'inventory'),
        ('处方历史', 'history')
    ]
    
    def __init__(self, parent=None, version_text=''):
        super().__init__(parent)
        self.version_text = version_text
        self.nav_buttons = []
        self.setObjectName('sidebar')
        self.init_ui()
    
    def _get_font(self, size, bold=False):
        font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
        font_db = QFontDatabase()
        if "Microsoft YaHei" not in font_db.families():
            font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
        return font
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        brand_container = QWidget()
        brand_container.setObjectName('brand_container')
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(20, 25, 20, 25)
        brand_layout.setSpacing(0)
        
        brand_title = QLabel('中药材管理系统')
        brand_title.setObjectName('brand_title')
        brand_title.setAlignment(Qt.AlignCenter)
        brand_title.setFont(self._get_font(14, bold=True))
        
        brand_layout.addWidget(brand_title)
        layout.addWidget(brand_container)
        
        separator = QFrame()
        separator.setObjectName('sidebar_separator')
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 15, 12, 15)
        nav_layout.setSpacing(4)
        
        for text, name in self.NAV_ITEMS:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName('nav_btn')
            btn.setFont(self._get_font(11))
            btn.clicked.connect(lambda checked, n=name: self._on_nav_clicked(n))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addWidget(nav_container)
        layout.addStretch()
        
        import_btn = QPushButton('批量导入药材')
        import_btn.setObjectName('import_btn')
        import_btn.setFont(self._get_font(11, bold=True))
        import_btn.clicked.connect(self.import_clicked.emit)
        layout.addWidget(import_btn)
        
        version_label = QLabel(self.version_text)
        version_label.setObjectName('version_label')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(self._get_font(9))
        layout.addWidget(version_label)
    
    def _on_nav_clicked(self, name):
        for i, (_, nav_name) in enumerate(self.NAV_ITEMS):
            self.nav_buttons[i].setChecked(nav_name == name)
        self.nav_clicked.emit(name)
    
    def set_current_nav(self, name):
        for i, (_, nav_name) in enumerate(self.NAV_ITEMS):
            self.nav_buttons[i].setChecked(nav_name == name)
    
    def set_fixed_width(self, width):
        self.setFixedWidth(width)
        self.setMinimumWidth(width)
