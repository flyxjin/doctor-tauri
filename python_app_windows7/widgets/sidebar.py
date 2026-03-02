# -*- coding: utf-8 -*-
"""
侧边栏导航 - 简约设计
清晰、易用、符合 WCAG 标准
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase

from utils.style import UIStyles


def get_font(size: int, bold: bool = False) -> QFont:
    """获取系统字体"""
    font = QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal)
    font_db = QFontDatabase()
    if "Segoe UI" not in font_db.families():
        font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
        if "Microsoft YaHei" not in font_db.families():
            font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
    return font


class SidebarWidget(QWidget):
    """
    侧边栏导航组件
    
    设计规范:
    - 字号：14px (符合 WCAG AA)
    - 对比度：≥ 4.5:1
    - 菜单项高度：44px
    - 间距：4px
    """
    
    nav_clicked = pyqtSignal(str)
    import_clicked = pyqtSignal()
    
    NAV_ITEMS = [
        ('数据统计', 'dashboard'),
        ('药材管理', 'medicine'),
        ('开处方', 'prescription'),
        ('库存管理', 'inventory'),
        ('处方历史', 'history'),
        ('处方模板', 'template'),
        ('患者管理', 'patient'),
        ('打印设置', 'print'),
    ]
    
    def __init__(self, parent=None, version_text=''):
        super().__init__(parent)
        self.version_text = version_text
        self.nav_buttons = {}
        self.setObjectName('sidebar')
        self._init_ui()
        
    def _init_ui(self):
        c = UIStyles.COLORS
        f = UIStyles.FONT
        s = UIStyles.SPACING
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 品牌区域
        brand_container = QWidget()
        brand_container.setObjectName('brand_container')
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(s['md'], s['lg'], s['md'], s['lg'])
        brand_layout.setSpacing(s['xs'])
        
        brand_title = QLabel('中药材管理系统')
        brand_title.setObjectName('brand_title')
        brand_title.setAlignment(Qt.AlignCenter)
        brand_title.setFont(get_font(f['size_title'], bold=True))
        
        brand_layout.addWidget(brand_title)
        
        main_layout.addWidget(brand_container)
        
        # 分隔线
        separator = QFrame()
        separator.setObjectName('sidebar_separator')
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 导航项
        nav_container = QWidget()
        nav_container.setStyleSheet('background: transparent;')
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, s['sm'], 0, s['sm'])
        nav_layout.setSpacing(s['xs'])
        
        for text, name in self.NAV_ITEMS:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName('nav_btn')
            btn.setFont(get_font(f['size_base']))
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, n=name: self._on_nav_clicked(n))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        main_layout.addWidget(nav_container)
        main_layout.addStretch()
        
        # 导入按钮
        import_btn = QPushButton('批量导入药材')
        import_btn.setObjectName('import_btn')
        import_btn.setFont(get_font(f['size_base'], bold=True))
        import_btn.setMinimumHeight(40)
        import_btn.clicked.connect(self.import_clicked.emit)
        main_layout.addWidget(import_btn)
        
        # 版本标签
        version_label = QLabel(self.version_text)
        version_label.setObjectName('version_label')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(get_font(f['size_small']))
        main_layout.addWidget(version_label)
        
    def _on_nav_clicked(self, name):
        for nav_name, btn in self.nav_buttons.items():
            btn.setChecked(nav_name == name)
        self.nav_clicked.emit(name)
        
    def set_current_nav(self, name):
        for nav_name, btn in self.nav_buttons.items():
            btn.setChecked(nav_name == name)
            
    def set_fixed_width(self, width):
        self.setFixedWidth(width)
        self.setMinimumWidth(width)
