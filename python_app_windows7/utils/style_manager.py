# -*- coding: utf-8 -*-
"""
样式管理器 - Windows 7兼容版本
提供统一的样式定义和管理
白底黑字风格，按钮使用黑色边框
"""


class StyleManager:
    """
    统一样式管理器 - 白底黑字风格
    
    颜色设计原则:
    1. 主背景: 白色 (#ffffff)
    2. 次背景: 浅灰 (#f5f5f5)
    3. 主文字: 黑色 (#000000)
    4. 次文字: 深灰 (#333333)
    5. 按钮: 白底黑边框
    """
    
    COLORS = {
        'primary': '#000000',
        'primary_hover': '#333333',
        'primary_active': '#000000',
        'sidebar_bg': '#ffffff',
        'sidebar_text': '#000000',
        'sidebar_text_secondary': '#666666',
        'sidebar_text_active': '#000000',
        'sidebar_border': '#e0e0e0',
        'bg_main': '#f5f5f5',
        'bg_card': '#ffffff',
        'text_main': '#000000',
        'text_primary': '#1a1a1a',
        'text_secondary': '#333333',
        'text_hint': '#666666',
        'border': '#000000',
        'border_light': '#e0e0e0',
        'success': '#52c41a',
        'warning': '#faad14',
        'error': '#ff4d4f',
        'button_bg': '#ffffff',
        'button_text': '#000000',
        'button_border': '#000000',
        'button_hover': '#f0f0f0',
        'nav_active_bg': '#000000',
        'nav_active_text': '#ffffff',
    }
    
    FONT_FAMILY = '"Microsoft YaHei", "SimSun", sans-serif'
    
    @classmethod
    def get_colors(cls):
        return cls.COLORS.copy()
    
    @classmethod
    def get_font_family(cls):
        return cls.FONT_FAMILY
    
    @classmethod
    def get_main_window_style(cls, base_size):
        c = cls.COLORS
        font_family = cls.FONT_FAMILY
        
        body_size = base_size
        small_size = int(base_size * 0.9)
        tiny_size = int(base_size * 0.85)
        button_size = int(base_size * 1.0)
        
        return f'''
            QMainWindow {{
                background-color: {c['bg_main']};
            }}
            QLabel {{
                font-size: {body_size}px;
                color: {c['text_main']};
                font-family: {font_family};
            }}
            QFrame#sidebar {{
                background-color: {c['sidebar_bg']};
                border-right: 1px solid {c['sidebar_border']};
            }}
            QWidget#brand_container {{
                background-color: {c['sidebar_bg']};
                border-bottom: 1px solid {c['sidebar_border']};
            }}
            QLabel#brand_title {{
                color: {c['sidebar_text']};
                font-size: {int(base_size * 1.3)}px;
                font-weight: bold;
                font-family: {font_family};
            }}
            QFrame#sidebar_separator {{
                background-color: {c['sidebar_border']};
            }}
            QPushButton#nav_btn {{
                background-color: {c['button_bg']};
                color: {c['button_text']};
                text-align: left;
                padding: 12px 20px;
                border-radius: 4px;
                margin: 2px 10px;
                font-size: {button_size}px;
                font-weight: normal;
                border: 1px solid {c['sidebar_border']};
                font-family: {font_family};
            }}
            QPushButton#nav_btn:hover {{
                background-color: {c['button_hover']};
                border-color: {c['button_border']};
            }}
            QPushButton#nav_btn:checked {{
                background-color: {c['nav_active_bg']};
                color: {c['nav_active_text']};
                font-weight: bold;
                border: 1px solid {c['nav_active_bg']};
            }}
            QPushButton#import_btn {{
                background-color: {c['button_bg']};
                color: {c['button_text']};
                text-align: center;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: {button_size}px;
                border: 2px solid {c['button_border']};
                font-family: {font_family};
            }}
            QPushButton#import_btn:hover {{
                background-color: {c['button_hover']};
            }}
            QPushButton#import_btn:pressed {{
                background-color: {c['nav_active_bg']};
                color: {c['nav_active_text']};
            }}
            QLabel#version_label {{
                color: {c['text_hint']};
                font-size: {tiny_size}px;
                padding: 8px;
                font-family: {font_family};
            }}
            QFrame#content_area {{
                background-color: {c['bg_main']};
            }}
            QFrame#card_container {{
                background-color: {c['bg_card']};
                border-radius: 4px;
                border: 1px solid {c['border_light']};
            }}
            QPushButton {{
                background-color: {c['button_bg']};
                color: {c['button_text']};
                border: 1px solid {c['button_border']};
                padding: 6px 12px;
                border-radius: 4px;
                font-size: {button_size}px;
                min-height: 28px;
                font-weight: normal;
                font-family: {font_family};
            }}
            QPushButton:hover {{
                background-color: {c['button_hover']};
                border-color: {c['button_border']};
            }}
            QPushButton:pressed {{
                background-color: {c['nav_active_bg']};
                color: {c['nav_active_text']};
            }}
            QPushButton:disabled {{
                background-color: #f5f5f5;
                color: #999999;
                border-color: #cccccc;
            }}
            QTableWidget {{
                font-size: {body_size}px;
                gridline-color: {c['border_light']};
                border: 1px solid {c['border_light']};
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #fafafa;
                font-family: {font_family};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {c['border_light']};
                color: {c['text_main']};
            }}
            QTableWidget::item:selected {{
                background-color: #e0e0e0;
                color: {c['text_main']};
                outline: none;
            }}
            QHeaderView::section {{
                font-size: {button_size}px;
                font-weight: bold;
                padding: 10px 8px;
                background-color: #fafafa;
                border: none;
                border-bottom: 1px solid {c['border_light']};
                border-right: 1px solid {c['border_light']};
                color: {c['text_main']};
                text-align: left;
                font-family: {font_family};
            }}
            QLineEdit, QComboBox, QTextEdit {{
                font-size: {body_size}px;
                padding: 6px 10px;
                border: 1px solid {c['button_border']};
                border-radius: 4px;
                background-color: white;
                color: {c['text_main']};
                font-family: {font_family};
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                border: 2px solid {c['button_border']};
                outline: none;
            }}
            QLineEdit:hover, QComboBox:hover {{
                border-color: {c['button_border']};
            }}
            QScrollBar:vertical {{
                width: 10px;
                background-color: transparent;
                margin: 0;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #c1c1c1;
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #a8a8a8;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QGroupBox {{
                border: 1px solid {c['border_light']};
                border-radius: 4px;
                margin-top: 16px;
                font-weight: bold;
                font-size: {int(base_size * 1.2)}px;
                color: {c['text_main']};
                padding-top: 12px;
                background-color: white;
                font-family: {font_family};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {c['text_main']};
            }}
            QMessageBox {{
                background-color: white;
                font-size: {body_size}px;
                font-family: {font_family};
            }}
            QMessageBox QLabel {{
                color: {c['text_main']};
                min-width: 50px;
            }}
            QMessageBox QPushButton {{
                min-width: 80px;
                padding: 6px 12px;
            }}
        '''
    
    @classmethod
    def get_menu_bar_style(cls):
        return """
            QMenuBar {
                background-color: #ffffff;
                color: #000000;
                padding: 0px 10px;
                border-bottom: 1px solid #e0e0e0;
            }
            QMenuBar::item {
                padding: 10px 16px;
                background-color: transparent;
                border-radius: 0;
            }
            QMenuBar::item:selected {
                background-color: #f0f0f0;
                color: #000000;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #000000;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
                color: #000000;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
        """
    
    @classmethod
    def get_status_bar_style(cls):
        return """
            QStatusBar {
                background-color: #ffffff;
                color: #333333;
                border-top: 1px solid #e0e0e0;
                padding: 4px 12px;
                font-size: 12px;
            }
        """


def get_style_manager():
    return StyleManager
