# -*- coding: utf-8 -*-
"""
简约专业 UI 样式系统
设计理念：简洁、大方、专业、易用
"""


class UIStyles:
    """UI 样式定义"""
    
    # 颜色方案 - 简约中性色调
    COLORS = {
        # 主色调 - 稳重的深蓝色
        'primary': '#2C5282',
        'primary_hover': '#1A365D',
        
        # 背景色 - 温暖的灰白色系
        'bg_main': '#F7FAFC',
        'bg_card': '#FFFFFF',
        'bg_sidebar': '#EDF2F7',
        
        # 文字色 - 清晰的灰色系
        'text_main': '#2D3748',
        'text_secondary': '#4A5568',
        'text_muted': '#718096',
        'text_light': '#FFFFFF',
        
        # 边框色
        'border': '#E2E8F0',
        'border_dark': '#CBD5E0',
        
        # 语义色 - 低饱和度
        'success': '#48BB78',
        'warning': '#ED8936',
        'error': '#F56565',
    }
    
    # 间距 - 8px 网格系统
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
    }
    
    # 圆角 - 适度圆角
    RADIUS = {
        'sm': 4,
        'md': 6,
        'lg': 8,
    }
    
    # 字体
    FONT = {
        'family': 'Microsoft YaHei, SimSun, sans-serif',
        'size_base': 14,
        'size_small': 12,
        'size_large': 16,
        'size_title': 18,
    }
    
    @classmethod
    def get_main_stylesheet(cls) -> str:
        """主界面样式表"""
        c = cls.COLORS
        r = cls.RADIUS
        s = cls.SPACING
        f = cls.FONT
        
        return f'''
            /* 主窗口 */
            QMainWindow {{
                background-color: {c['bg_main']};
            }}
            
            QWidget {{
                font-family: {f['family']};
                font-size: {f['size_base']}px;
                color: {c['text_main']};
            }}
            
            QLabel {{
                color: {c['text_main']};
                background: transparent;
                border: none;
            }}
            
            /* 侧边栏 - 简约灰色 */
            QFrame#sidebar {{
                background-color: {c['bg_sidebar']};
                border-right: 1px solid {c['border']};
            }}
            
            QWidget#brand_container {{
                background: transparent;
                border-bottom: 1px solid {c['border']};
                padding: 16px;
            }}
            
            QLabel#brand_title {{
                color: {c['text_main']};
                font-size: {f['size_title']}px;
                font-weight: bold;
            }}
            
            /* 导航按钮 */
            QPushButton#nav_btn {{
                background: transparent;
                color: {c['text_secondary']};
                border: none;
                border-radius: {r['md']}px;
                padding: 10px 16px;
                margin: 2px 8px;
                min-height: 40px;
                text-align: left;
            }}
            
            QPushButton#nav_btn:hover {{
                background-color: {c['border']};
                color: {c['text_main']};
            }}
            
            QPushButton#nav_btn:checked {{
                background-color: {c['primary']};
                color: {c['text_light']};
                font-weight: bold;
            }}
            
            /* 导入按钮 */
            QPushButton#import_btn {{
                background-color: {c['primary']};
                color: {c['text_light']};
                border: none;
                border-radius: {r['md']}px;
                padding: 10px 16px;
                min-height: 40px;
                font-weight: bold;
            }}
            
            QPushButton#import_btn:hover {{
                background-color: {c['primary_hover']};
            }}
            
            QLabel#version_label {{
                color: {c['text_muted']};
                font-size: {f['size_small']}px;
                padding: 8px;
            }}
            
            QFrame#sidebar_separator {{
                background-color: {c['border']};
                max-height: 1px;
            }}
            
            /* 内容区 */
            QFrame#content_area {{
                background-color: {c['bg_main']};
            }}
            
            /* 标准按钮 */
            QPushButton {{
                background-color: {c['bg_card']};
                color: {c['text_main']};
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                padding: 8px 16px;
                min-height: 36px;
            }}
            
            QPushButton:hover {{
                background-color: {c['border']};
            }}
            
            QPushButton:pressed {{
                background-color: {c['border_dark']};
            }}
            
            QPushButton:disabled {{
                color: {c['text_muted']};
                background-color: {c['bg_sidebar']};
                border-color: {c['border']};
            }}
            
            /* 输入框 */
            QLineEdit, QTextEdit {{
                padding: 8px 12px;
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                background-color: {c['bg_card']};
                color: {c['text_main']};
            }}
            
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {c['border']};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {c['primary']};
            }}
            
            /* 下拉框 */
            QComboBox {{
                padding: 8px 12px;
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                background-color: {c['bg_card']};
                min-height: 36px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {c['text_muted']};
                margin-right: 6px;
            }}
            
            /* 表格 */
            QTableWidget {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                background-color: {c['bg_card']};
                alternate-background-color: {c['bg_main']};
                gridline-color: transparent;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {c['border']};
            }}
            
            QTableWidget::item:hover {{
                background-color: {c['bg_sidebar']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {c['primary']}20;
                color: {c['text_main']};
            }}
            
            QHeaderView::section {{
                font-weight: bold;
                padding: 8px;
                background-color: {c['bg_sidebar']};
                border: none;
                border-bottom: 1px solid {c['border_dark']};
                color: {c['text_secondary']};
            }}
            
            QTableWidget QScrollBar:vertical {{
                width: 8px;
                background-color: transparent;
                border-radius: {r['sm']}px;
            }}
            
            QTableWidget QScrollBar::handle:vertical {{
                background-color: {c['border_dark']};
                border-radius: {r['sm']}px;
                min-height: 30px;
            }}
            
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            /* 分组框 */
            QGroupBox {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                margin-top: 16px;
                padding-top: 8px;
                font-weight: bold;
                background-color: {c['bg_card']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: {c['text_main']};
            }}
            
            /* 滚动条 */
            QScrollBar:vertical {{
                width: 8px;
                background-color: transparent;
                border-radius: {r['sm']}px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {c['border_dark']};
                border-radius: {r['sm']}px;
                min-height: 30px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            /* 进度条 */
            QProgressBar {{
                border: none;
                border-radius: {r['sm']}px;
                background-color: {c['border']};
                height: 6px;
                text-align: center;
                color: transparent;
            }}
            
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: {r['sm']}px;
            }}
            
            /* 复选框 */
            QCheckBox {{
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c['border_dark']};
                border-radius: 3px;
                background-color: {c['bg_card']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
            }}
            
            /* 选项卡 */
            QTabWidget::pane {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                background-color: {c['bg_card']};
            }}
            
            QTabBar::tab {{
                background: transparent;
                color: {c['text_secondary']};
                padding: 8px 16px;
                border-bottom: 2px solid transparent;
            }}
            
            QTabBar::tab:hover {{
                color: {c['text_main']};
            }}
            
            QTabBar::tab:selected {{
                color: {c['primary']};
                border-bottom: 2px solid {c['primary']};
                font-weight: bold;
            }}
            
            /* 工具提示 */
            QToolTip {{
                background-color: {c['bg_card']};
                color: {c['text_main']};
                padding: 6px 10px;
                border-radius: {r['sm']}px;
                border: 1px solid {c['border_dark']};
                font-size: {f['size_small']}px;
            }}
            
            /* 菜单栏 */
            QMenuBar {{
                background-color: {c['bg_card']};
                border-bottom: 1px solid {c['border']};
            }}
            
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: {r['sm']}px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {c['bg_sidebar']};
            }}
            
            QMenu {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 16px;
                border-radius: {r['sm']}px;
            }}
            
            QMenu::item:selected {{
                background-color: {c['bg_sidebar']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {c['border']};
                margin: 4px 8px;
            }}
            
            /* 状态栏 */
            QStatusBar {{
                background-color: {c['bg_card']};
                border-top: 1px solid {c['border']};
                padding: 4px 12px;
                font-size: {f['size_small']}px;
            }}
            
            /* 消息框 */
            QMessageBox {{
                background-color: {c['bg_card']};
            }}
            
            QMessageBox QLabel {{
                color: {c['text_main']};
                min-width: 200px;
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
                padding: 8px 16px;
            }}
        '''
    
    @classmethod
    def get_card_style(cls) -> str:
        """卡片样式"""
        c = cls.COLORS
        r = cls.RADIUS
        
        return f'''
            QFrame {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: {r['lg']}px;
                padding: 16px;
            }}
        '''
    
    @classmethod
    def get_stat_card_style(cls, variant: str = 'default') -> str:
        """统计卡片样式"""
        c = cls.COLORS
        r = cls.RADIUS
        
        styles = {
            'default': f'''
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
            ''',
            'primary': f'''
                background-color: {c['primary']}10;
                border: 1px solid {c['primary']};
            ''',
            'success': f'''
                background-color: {c['success']}10;
                border: 1px solid {c['success']};
            ''',
            'warning': f'''
                background-color: {c['warning']}10;
                border: 1px solid {c['warning']};
            ''',
            'error': f'''
                background-color: {c['error']}10;
                border: 1px solid {c['error']};
            ''',
        }
        
        return f'''
            QFrame#stat_card {{
                {styles.get(variant, styles['default'])}
                border-radius: {r['lg']}px;
            }}
            QLabel#stat_value {{
                color: {c['text_main']};
                font-size: 24px;
                font-weight: bold;
            }}
            QLabel#stat_title {{
                color: {c['text_secondary']};
                font-size: 13px;
            }}
            QLabel#stat_subtitle {{
                color: {c['text_muted']};
                font-size: 11px;
            }}
        '''
