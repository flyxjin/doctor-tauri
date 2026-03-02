# -*- coding: utf-8 -*-
"""
侧边栏导航 - 现代简约设计
清晰、易用、符合 WCAG 标准
自适应布局，支持不同屏幕尺寸
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QFontDatabase, QPainter, QColor

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


class NavButton(QPushButton):
    """导航按钮组件 - 支持选中状态和悬停效果"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._is_hovered = False
        self._is_checked = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        c = UIStyles.COLORS
        dt = UIStyles.DT
        
        rect = self.rect()
        margin = 8
        inner_rect = rect.adjusted(margin, 2, -margin, -2)
        
        if self._is_checked:
            painter.fillRect(inner_rect, QColor(dt.COLORS['primary']['default']))
        elif self._is_hovered:
            painter.fillRect(inner_rect, QColor(dt.COLORS['neutral']['gray']['200']))
        else:
            painter.fillRect(inner_rect, QColor(255, 255, 255, 0))
        
        text_color = c['text_light'] if self._is_checked else c['text_main']
        painter.setPen(QColor(text_color))
        painter.setFont(self.font())
        
        text_rect = inner_rect.adjusted(16, 0, 0, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())
        
        painter.end()
    
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        
    def setChecked(self, checked):
        self._is_checked = checked
        self.update()


class SidebarWidget(QWidget):
    """
    侧边栏导航组件 - 现代设计
    
    设计规范:
    - 默认宽度: 200px (自适应 160-240px)
    - 字号: 14px (符合 WCAG AA)
    - 对比度: ≥ 4.5:1
    - 菜单项高度: 42px
    """
    
    nav_clicked = pyqtSignal(str)
    
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
        self._current_width = 200
        self.setObjectName('sidebar')
        self._init_ui()
        
    def _init_ui(self):
        c = UIStyles.COLORS
        dt = UIStyles.DT
        f = UIStyles.FONT
        s = UIStyles.SPACING

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(dt.COLORS['neutral']['gray']['50']))
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        brand_container = QWidget()
        brand_container.setMinimumHeight(70)
        brand_container.setMaximumHeight(80)
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(s['4'], s['5'], s['4'], s['5'])
        brand_layout.setSpacing(s['1'])
        
        brand_title = QLabel('中药材管理系统')
        brand_title.setObjectName('brand_title')
        brand_title.setAlignment(Qt.AlignCenter)
        brand_title.setFont(get_font(f['size_large'], bold=True))
        brand_title.setStyleSheet(f'''
            QLabel#brand_title {{
                color: {c['text_main']};
                background: transparent;
                border: none;
            }}
        ''')
        
        brand_layout.addWidget(brand_title)
        main_layout.addWidget(brand_container)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f'''
            QFrame {{
                background-color: {c['border']};
                border: none;
                margin: 0 12px;
            }}
        ''')
        main_layout.addWidget(separator)

        nav_container = QWidget()
        nav_container.setStyleSheet('background: transparent;')
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, s['3'], 0, s['3'])
        nav_layout.setSpacing(2)
        
        for text, name in self.NAV_ITEMS:
            btn = NavButton(text)
            btn.setFont(get_font(f['size_base']))
            btn.clicked.connect(lambda checked, n=name: self._on_nav_clicked(n))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        main_layout.addWidget(nav_container)
        main_layout.addStretch()

        version_label = QLabel(self.version_text)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(get_font(f['size_small']))
        version_label.setStyleSheet(f'''
            QLabel {{
                color: {c['text_muted']};
                background: transparent;
                border: none;
                padding: 8px;
            }}
        ''')
        main_layout.addWidget(version_label)
        
    def _on_nav_clicked(self, name):
        for nav_name, btn in self.nav_buttons.items():
            btn.setChecked(nav_name == name)
        self.nav_clicked.emit(name)
        
    def set_current_nav(self, name):
        for nav_name, btn in self.nav_buttons.items():
            btn.setChecked(nav_name == name)
            
    def set_fixed_width(self, width):
        self._current_width = width
        self.setFixedWidth(width)
        self.setMinimumWidth(width)
    
    def update_for_window_size(self, window_width: int):
        """根据窗口大小自适应调整侧边栏宽度"""
        if window_width < 1200:
            new_width = 170
        elif window_width < 1400:
            new_width = 190
        else:
            new_width = 210
            
        if new_width != self._current_width:
            self._current_width = new_width
            self.setFixedWidth(new_width)
