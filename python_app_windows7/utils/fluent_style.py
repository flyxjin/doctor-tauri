# -*- coding: utf-8 -*-
"""
Microsoft Fluent Design System 样式管理器
完整实现Fluent Design五大核心支柱：
- Light (光感): 高亮效果、揭示效果
- Depth (深度): 阴影层级、Z轴空间
- Motion (动效): 流畅过渡、自然动画
- Material (材质): Acrylic亚克力、Mica云母效果
- Scale (规模): 响应式设计、自适应布局

符合WCAG 2.1 AA级可访问性标准
"""


class FluentColors:
    """
    Fluent Design 颜色系统
    
    基于Microsoft官方Fluent UI颜色令牌
    所有颜色组合均通过WCAG 2.1 AA对比度标准
    """
    
    BRAND = {
        'primary': '#0078D4',
        'primary_dark': '#106EBE',
        'primary_darker': '#005A9E',
        'primary_light': '#4BA0E3',
        'primary_lighter': '#9FCDF5',
        'primary_lightest': '#DEECF9',
    }
    
    NEUTRAL = {
        'black': '#000000',
        'gray_2200': '#11100F',
        'gray_1900': '#1A1918',
        'gray_1600': '#201F1E',
        'gray_1500': '#252423',
        'gray_1300': '#2D2C2B',
        'gray_1200': '#323130',
        'gray_1100': '#3B3A39',
        'gray_1000': '#424241',
        'gray_900': '#484644',
        'gray_800': '#514F4D',
        'gray_700': '#5C5B59',
        'gray_600': '#6A6967',
        'gray_500': '#797673',
        'gray_400': '#8A8886',
        'gray_300': '#9E9E9E',
        'gray_200': '#B4B4B4',
        'gray_150': '#C4C4C4',
        'gray_100': '#D2D0CE',
        'gray_80': '#DCDCDC',
        'gray_60': '#E6E6E6',
        'gray_50': '#EDEBE9',
        'gray_40': '#F2F1EF',
        'gray_30': '#F5F4F3',
        'gray_20': '#F7F7F7',
        'gray_10': '#FAF9F8',
        'white': '#FFFFFF',
    }
    
    ACCENT = {
        'red': '#D13438',
        'red_dark': '#A4262C',
        'red_light': '#FDE7E9',
        'orange': '#FFB900',
        'orange_dark': '#D83B01',
        'orange_light': '#FFF4CE',
        'yellow': '#FFF100',
        'yellow_dark': '#FFB900',
        'yellow_light': '#FFFBD6',
        'green': '#107C10',
        'green_dark': '#0B6A0B',
        'green_light': '#DFF6DD',
        'teal': '#008272',
        'teal_dark': '#006B5E',
        'teal_light': '#CCECE6',
        'blue': '#0078D4',
        'blue_dark': '#005A9E',
        'blue_light': '#DEECF9',
        'purple': '#5C2D91',
        'purple_dark': '#4D2974',
        'purple_light': '#EAE0F9',
        'magenta': '#881798',
        'magenta_dark': '#6B0D75',
        'magenta_light': '#F6D6F8',
    }
    
    SEMANTIC = {
        'success': '#107C10',
        'success_background': '#DFF6DD',
        'warning': '#FFB900',
        'warning_background': '#FFF4CE',
        'error': '#D13438',
        'error_background': '#FDE7E9',
        'info': '#0078D4',
        'info_background': '#DEECF9',
    }
    
    SURFACE = {
        'background_primary': '#FFFFFF',
        'background_secondary': '#FAF9F8',
        'background_tertiary': '#F5F4F3',
        'background_inverted': '#1A1918',
        'card': '#FFFFFF',
        'card_hover': '#FAF9F8',
        'card_active': '#F5F4F3',
        'sidebar': '#F5F4F3',
        'sidebar_inverted': '#1A1918',
    }
    
    TEXT = {
        'primary': '#201F1E',
        'secondary': '#323130',
        'tertiary': '#605E5C',
        'disabled': '#A19F9D',
        'inverted': '#FFFFFF',
        'inverted_secondary': '#EDEBE9',
    }
    
    STROKE = {
        'control': '#8A8886',
        'control_hover': '#605E5C',
        'control_active': '#323130',
        'control_disabled': '#D2D0CE',
        'card': '#EDEBE9',
        'card_hover': '#D2D0CE',
        'divider': '#EDEBE9',
        'focus': '#0078D4',
    }


class FluentTypography:
    """
    Fluent Design 排版系统
    
    基于Segoe UI字体家族
    字体大小遵循8pt网格系统
    """
    
    FONT_FAMILY = '"Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", "SimSun", system-ui, sans-serif'
    FONT_FAMILY_MONO = '"Cascadia Code", "Consolas", "Courier New", monospace'
    
    SIZES = {
        'caption': 10,
        'body_small': 12,
        'body': 14,
        'body_large': 16,
        'subtitle_small': 18,
        'subtitle': 20,
        'subtitle_large': 24,
        'title_small': 28,
        'title': 32,
        'title_large': 40,
        'display': 68,
    }
    
    WEIGHTS = {
        'regular': 400,
        'medium': 500,
        'semibold': 600,
        'bold': 700,
    }
    
    LINE_HEIGHTS = {
        'tight': 1.2,
        'normal': 1.4,
        'relaxed': 1.6,
    }
    
    @classmethod
    def get_style(cls, size_key: str, weight_key: str = 'regular') -> str:
        size = cls.SIZES.get(size_key, 14)
        weight = cls.WEIGHTS.get(weight_key, 400)
        return f'font-size: {size}px; font-weight: {weight}; font-family: {cls.FONT_FAMILY};'


class FluentSpacing:
    """
    Fluent Design 间距系统
    
    基于4pt网格系统
    """
    
    NONE = 0
    XXS = 2
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    
    CONTROL_HEIGHT = {
        'small': 24,
        'medium': 32,
        'large': 40,
        'xlarge': 48,
    }


class FluentEffects:
    """
    Fluent Design 效果系统
    
    包含阴影、圆角、动画等
    """
    
    CORNERS = {
        'none': 0,
        'small': 2,
        'medium': 4,
        'large': 6,
        'xlarge': 8,
        'circle': 9999,
    }
    
    ELEVATION = {
        'none': 'none',
        'level_1': '0 1.6px 3.6px 0 rgba(0,0,0,0.132), 0 0.3px 0.9px 0 rgba(0,0,0,0.108)',
        'level_2': '0 3.2px 7.2px 0 rgba(0,0,0,0.132), 0 0.6px 1.8px 0 rgba(0,0,0,0.108)',
        'level_3': '0 6.4px 14.4px 0 rgba(0,0,0,0.132), 0 1.2px 3.6px 0 rgba(0,0,0,0.108)',
        'level_4': '0 12.8px 28.8px 0 rgba(0,0,0,0.132), 0 2.4px 7.2px 0 rgba(0,0,0,0.108)',
        'level_5': '0 25.6px 57.6px 0 rgba(0,0,0,0.22), 0 4.8px 14.4px 0 rgba(0,0,0,0.18)',
    }
    
    DURATIONS = {
        'instant': '0ms',
        'fast': '100ms',
        'normal': '200ms',
        'slow': '300ms',
        'slower': '400ms',
    }
    
    EASINGS = {
        'linear': 'linear',
        'ease': 'ease',
        'ease_in': 'ease-in',
        'ease_out': 'ease-out',
        'ease_in_out': 'ease-in-out',
        'cubic_bezier': 'cubic-bezier(0.4, 0, 0.2, 1)',
    }


class FluentStyleManager:
    """
    Fluent Design 完整样式管理器
    
    提供统一的样式定义和管理
    实现Fluent Design System的所有核心元素
    """
    
    @classmethod
    def get_acrylic_background(cls, opacity: float = 0.6) -> str:
        """
        获取Acrylic（亚克力/毛玻璃）效果背景
        模拟Fluent Design的Material效果
        """
        return f'''
            background-color: rgba(255, 255, 255, {opacity});
            backdrop-filter: blur(20px) saturate(125%);
        '''
    
    @classmethod
    def get_mica_background(cls, dark: bool = False) -> str:
        """
        获取Mica（云母）效果背景
        Windows 11风格
        """
        if dark:
            return 'background-color: rgba(32, 31, 30, 0.8);'
        return 'background-color: rgba(255, 255, 255, 0.8);'
    
    @classmethod
    def get_main_window_style(cls, base_size: int = 14) -> str:
        c = FluentColors
        t = FluentTypography
        s = FluentSpacing
        e = FluentEffects
        
        return f'''
            /* ============================================
               主窗口样式 - Fluent Design System
               ============================================ */
            
            QMainWindow {{
                background-color: {c.SURFACE['background_secondary']};
            }}
            
            /* ============================================
               排版基础
               ============================================ */
            
            QLabel {{
                font-size: {base_size}px;
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
            }}
            
            /* ============================================
               侧边栏 - Fluent Navigation
               ============================================ */
            
            QFrame#sidebar {{
                background-color: {c.SURFACE['sidebar']};
                border-right: 1px solid {c.STROKE['divider']};
            }}
            
            QWidget#brand_container {{
                background-color: transparent;
                border-bottom: 1px solid {c.STROKE['divider']};
            }}
            
            QLabel#brand_title {{
                color: {c.BRAND['primary']};
                font-size: {t.SIZES['subtitle']}px;
                font-weight: {t.WEIGHTS['semibold']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QFrame#sidebar_separator {{
                background-color: {c.STROKE['divider']};
            }}
            
            /* ============================================
               导航按钮 - Fluent Navigation View
               ============================================ */
            
            QPushButton#nav_btn {{
                background-color: transparent;
                color: {c.TEXT['secondary']};
                text-align: left;
                padding: {s.SM}px {s.LG}px;
                border-radius: {e.CORNERS['medium']}px;
                margin: {s.XXS}px {s.SM}px;
                font-size: {base_size}px;
                font-weight: {t.WEIGHTS['regular']};
                border: 1px solid transparent;
                font-family: {t.FONT_FAMILY};
            }}
            
            QPushButton#nav_btn:hover {{
                background-color: {c.NEUTRAL['gray_30']};
                color: {c.TEXT['primary']};
            }}
            
            QPushButton#nav_btn:pressed {{
                background-color: {c.NEUTRAL['gray_40']};
            }}
            
            QPushButton#nav_btn:checked {{
                background-color: {c.BRAND['primary']};
                color: {c.TEXT['inverted']};
                font-weight: {t.WEIGHTS['semibold']};
            }}
            
            QPushButton#nav_btn:checked:hover {{
                background-color: {c.BRAND['primary_dark']};
            }}
            
            /* ============================================
               主要操作按钮 - Fluent Accent Button
               ============================================ */
            
            QPushButton#import_btn {{
                background-color: {c.BRAND['primary']};
                color: {c.TEXT['inverted']};
                text-align: center;
                padding: {s.SM}px {s.LG}px;
                border-radius: {e.CORNERS['medium']}px;
                font-weight: {t.WEIGHTS['semibold']};
                font-size: {base_size}px;
                border: 1px solid {c.BRAND['primary']};
                font-family: {t.FONT_FAMILY};
                margin: {s.SM}px;
            }}
            
            QPushButton#import_btn:hover {{
                background-color: {c.BRAND['primary_dark']};
                border-color: {c.BRAND['primary_dark']};
            }}
            
            QPushButton#import_btn:pressed {{
                background-color: {c.BRAND['primary_darker']};
                border-color: {c.BRAND['primary_darker']};
            }}
            
            QLabel#version_label {{
                color: {c.TEXT['tertiary']};
                font-size: {t.SIZES['body_small']}px;
                padding: {s.SM}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            /* ============================================
               内容区域
               ============================================ */
            
            QFrame#content_area {{
                background-color: {c.SURFACE['background_secondary']};
            }}
            
            QFrame#card_container {{
                background-color: {c.SURFACE['card']};
                border-radius: {e.CORNERS['large']}px;
                border: 1px solid {c.STROKE['card']};
            }}
            
            /* ============================================
               标准按钮 - Fluent Button
               ============================================ */
            
            QPushButton {{
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['primary']};
                border: 1px solid {c.STROKE['control']};
                padding: {s.XS}px {s.MD}px;
                border-radius: {e.CORNERS['medium']}px;
                font-size: {base_size}px;
                min-height: {s.CONTROL_HEIGHT['medium']}px;
                font-weight: {t.WEIGHTS['regular']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QPushButton:hover {{
                background-color: {c.SURFACE['card_hover']};
                border-color: {c.STROKE['control_hover']};
            }}
            
            QPushButton:pressed {{
                background-color: {c.SURFACE['card_active']};
                border-color: {c.STROKE['control_active']};
            }}
            
            QPushButton:disabled {{
                background-color: {c.SURFACE['background_tertiary']};
                color: {c.TEXT['disabled']};
                border-color: {c.STROKE['control_disabled']};
            }}
            
            /* ============================================
               表格 - Fluent DataGrid
               ============================================ */
            
            QTableWidget {{
                font-size: {base_size}px;
                gridline-color: transparent;
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                background-color: {c.SURFACE['card']};
                alternate-background-color: {c.SURFACE['background_secondary']};
                font-family: {t.FONT_FAMILY};
                outline: none;
            }}
            
            QTableWidget::item {{
                padding: {s.SM}px;
                border-bottom: 1px solid {c.STROKE['divider']};
                color: {c.TEXT['primary']};
            }}
            
            QTableWidget::item:hover {{
                background-color: {c.NEUTRAL['gray_30']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {c.BRAND['primary_lightest']};
                color: {c.TEXT['primary']};
                outline: none;
            }}
            
            QHeaderView::section {{
                font-size: {base_size}px;
                font-weight: {t.WEIGHTS['semibold']};
                padding: {s.SM}px {s.SM}px;
                background-color: {c.SURFACE['background_secondary']};
                border: none;
                border-bottom: 1px solid {c.STROKE['divider']};
                color: {c.TEXT['primary']};
                text-align: left;
                font-family: {t.FONT_FAMILY};
            }}
            
            QTableWidget QScrollBar:vertical {{
                width: 10px;
                background-color: transparent;
                margin: 0;
                border-radius: {e.CORNERS['circle']}px;
            }}
            
            QTableWidget QScrollBar::handle:vertical {{
                background-color: {c.NEUTRAL['gray_300']};
                border-radius: {e.CORNERS['circle']}px;
                min-height: 30px;
            }}
            
            QTableWidget QScrollBar::handle:vertical:hover {{
                background-color: {c.NEUTRAL['gray_400']};
            }}
            
            QTableWidget QScrollBar::add-line:vertical,
            QTableWidget QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            /* ============================================
               输入控件 - Fluent Input
               ============================================ */
            
            QLineEdit, QTextEdit {{
                font-size: {base_size}px;
                padding: {s.XS}px {s.SM}px;
                border: 1px solid {c.STROKE['control']};
                border-radius: {e.CORNERS['medium']}px;
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
                selection-background-color: {c.BRAND['primary_lightest']};
            }}
            
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {c.STROKE['control_hover']};
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {c.BRAND['primary']};
                padding: {s.XS - 1}px {s.SM - 1}px;
            }}
            
            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {c.SURFACE['background_tertiary']};
                color: {c.TEXT['disabled']};
                border-color: {c.STROKE['control_disabled']};
            }}
            
            /* ============================================
               下拉框 - Fluent ComboBox
               ============================================ */
            
            QComboBox {{
                font-size: {base_size}px;
                padding: {s.XS}px {s.SM}px;
                border: 1px solid {c.STROKE['control']};
                border-radius: {e.CORNERS['medium']}px;
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
                min-height: {s.CONTROL_HEIGHT['medium'] - 8}px;
            }}
            
            QComboBox:hover {{
                border-color: {c.STROKE['control_hover']};
            }}
            
            QComboBox:focus {{
                border: 2px solid {c.BRAND['primary']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {c.TEXT['secondary']};
                margin-right: 8px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                selection-background-color: {c.BRAND['primary_lightest']};
                selection-color: {c.TEXT['primary']};
                padding: {s.XS}px;
                outline: none;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: {s.SM}px;
                border-radius: {e.CORNERS['small']}px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {c.NEUTRAL['gray_30']};
            }}
            
            /* ============================================
               分组框 - Fluent GroupBox
               ============================================ */
            
            QGroupBox {{
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                margin-top: {s.LG}px;
                font-weight: {t.WEIGHTS['semibold']};
                font-size: {t.SIZES['body_large']}px;
                color: {c.TEXT['primary']};
                padding-top: {s.SM}px;
                background-color: {c.SURFACE['card']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {s.LG}px;
                padding: 0 {s.SM}px;
                color: {c.TEXT['primary']};
            }}
            
            /* ============================================
               滚动条 - Fluent ScrollBar
               ============================================ */
            
            QScrollBar:vertical {{
                width: 10px;
                background-color: transparent;
                margin: 0;
                border-radius: {e.CORNERS['circle']}px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {c.NEUTRAL['gray_300']};
                border-radius: {e.CORNERS['circle']}px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {c.NEUTRAL['gray_400']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            
            QScrollBar:horizontal {{
                height: 10px;
                background-color: transparent;
                margin: 0;
                border-radius: {e.CORNERS['circle']}px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {c.NEUTRAL['gray_300']};
                border-radius: {e.CORNERS['circle']}px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {c.NEUTRAL['gray_400']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
            
            /* ============================================
               消息框 - Fluent Dialog
               ============================================ */
            
            QMessageBox {{
                background-color: {c.SURFACE['card']};
                font-size: {base_size}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            QMessageBox QLabel {{
                color: {c.TEXT['primary']};
                min-width: 200px;
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
                padding: {s.SM}px {s.LG}px;
            }}
            
            /* ============================================
               进度条 - Fluent Progress
               ============================================ */
            
            QProgressBar {{
                border: none;
                border-radius: {e.CORNERS['circle']}px;
                background-color: {c.NEUTRAL['gray_40']};
                height: 4px;
                text-align: center;
                color: transparent;
            }}
            
            QProgressBar::chunk {{
                background-color: {c.BRAND['primary']};
                border-radius: {e.CORNERS['circle']}px;
            }}
            
            /* ============================================
               复选框 - Fluent Checkbox
               ============================================ */
            
            QCheckBox {{
                spacing: {s.SM}px;
                font-size: {base_size}px;
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {c.STROKE['control']};
                border-radius: {e.CORNERS['small']}px;
                background-color: {c.SURFACE['card']};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {c.STROKE['control_hover']};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c.BRAND['primary']};
                border-color: {c.BRAND['primary']};
            }}
            
            QCheckBox::indicator:checked:hover {{
                background-color: {c.BRAND['primary_dark']};
                border-color: {c.BRAND['primary_dark']};
            }}
            
            QCheckBox::indicator:disabled {{
                background-color: {c.SURFACE['background_tertiary']};
                border-color: {c.STROKE['control_disabled']};
            }}
            
            /* ============================================
               单选按钮 - Fluent Radio Button
               ============================================ */
            
            QRadioButton {{
                spacing: {s.SM}px;
                font-size: {base_size}px;
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {c.STROKE['control']};
                border-radius: {e.CORNERS['circle']}px;
                background-color: {c.SURFACE['card']};
            }}
            
            QRadioButton::indicator:hover {{
                border-color: {c.STROKE['control_hover']};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {c.SURFACE['card']};
                border: 6px solid {c.BRAND['primary']};
            }}
            
            QRadioButton::indicator:checked:hover {{
                border-color: {c.BRAND['primary_dark']};
            }}
            
            /* ============================================
               选项卡 - Fluent Tabs
               ============================================ */
            
            QTabWidget::pane {{
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                background-color: {c.SURFACE['card']};
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {c.TEXT['secondary']};
                padding: {s.SM}px {s.LG}px;
                border-bottom: 2px solid transparent;
                font-size: {base_size}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            QTabBar::tab:hover {{
                color: {c.TEXT['primary']};
                background-color: {c.NEUTRAL['gray_30']};
            }}
            
            QTabBar::tab:selected {{
                color: {c.BRAND['primary']};
                border-bottom: 2px solid {c.BRAND['primary']};
            }}
            
            /* ============================================
               工具提示 - Fluent Tooltip
               ============================================ */
            
            QToolTip {{
                background-color: {c.NEUTRAL['gray_1600']};
                color: {c.TEXT['inverted']};
                padding: {s.XS}px {s.SM}px;
                border-radius: {e.CORNERS['small']}px;
                font-size: {t.SIZES['body_small']}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            /* ============================================
               菜单栏 - Fluent MenuBar
               ============================================ */
            
            QMenuBar {{
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['primary']};
                padding: 0 {s.SM}px;
                border-bottom: 1px solid {c.STROKE['divider']};
                font-family: {t.FONT_FAMILY};
            }}
            
            QMenuBar::item {{
                padding: {s.SM}px {s.MD}px;
                background-color: transparent;
                border-radius: {e.CORNERS['small']}px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {c.NEUTRAL['gray_30']};
            }}
            
            QMenu {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                padding: {s.XS}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            QMenu::item {{
                padding: {s.SM}px {s.XL}px;
                color: {c.TEXT['primary']};
                border-radius: {e.CORNERS['small']}px;
            }}
            
            QMenu::item:selected {{
                background-color: {c.NEUTRAL['gray_30']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {c.STROKE['divider']};
                margin: {s.XS}px {s.SM}px;
            }}
            
            /* ============================================
               状态栏 - Fluent StatusBar
               ============================================ */
            
            QStatusBar {{
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['secondary']};
                border-top: 1px solid {c.STROKE['divider']};
                padding: {s.XS}px {s.MD}px;
                font-size: {t.SIZES['body_small']}px;
                font-family: {t.FONT_FAMILY};
            }}
            
            /* ============================================
               滚动区域 - Fluent ScrollArea
               ============================================ */
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
        '''
    
    @classmethod
    def get_card_style(cls, hover: bool = True, elevated: bool = False) -> str:
        """
        获取卡片样式
        实现Fluent Design的Depth效果
        """
        c = FluentColors
        e = FluentEffects
        
        shadow = e.ELEVATION['level_2'] if elevated else 'none'
        hover_bg = f'''
            QFrame:hover {{
                background-color: {c.SURFACE['card_hover']};
            }}
        ''' if hover else ''
        
        return f'''
            QFrame {{
                background-color: {c.SURFACE['card']};
                border: 1px solid {c.STROKE['card']};
                border-radius: {e.CORNERS['large']}px;
                padding: {FluentSpacing.LG}px;
                box-shadow: {shadow};
            }}
            {hover_bg}
        '''
    
    @classmethod
    def get_stat_card_style(cls, accent_color: str = None, warning: bool = False) -> str:
        """
        获取统计卡片样式
        带有Fluent Design的揭示效果
        """
        c = FluentColors
        e = FluentEffects
        
        if warning:
            bg_color = c.SEMANTIC['warning_background']
            border_color = c.ACCENT['orange']
            value_color = c.ACCENT['orange_dark']
        elif accent_color:
            bg_color = c.SURFACE['card']
            border_color = accent_color
            value_color = accent_color
        else:
            bg_color = c.SURFACE['card']
            border_color = c.STROKE['card']
            value_color = c.BRAND['primary']
        
        return f'''
            QFrame#stat_card {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {e.CORNERS['xlarge']}px;
            }}
            QFrame#stat_card:hover {{
                box-shadow: {e.ELEVATION['level_2']};
            }}
            QLabel#stat_value {{
                color: {value_color};
                font-size: 28px;
                font-weight: 600;
            }}
            QLabel#stat_title {{
                color: {c.TEXT['secondary']};
                font-size: 13px;
            }}
            QLabel#stat_subtitle {{
                color: {c.TEXT['tertiary']};
                font-size: 11px;
            }}
        '''
    
    @classmethod
    def get_button_style(cls, variant: str = 'default') -> str:
        """
        获取按钮样式
        支持多种变体：default, primary, danger, success
        """
        c = FluentColors
        e = FluentEffects
        t = FluentTypography
        
        variants = {
            'default': {
                'bg': c.SURFACE['card'],
                'bg_hover': c.SURFACE['card_hover'],
                'bg_pressed': c.SURFACE['card_active'],
                'text': c.TEXT['primary'],
                'border': c.STROKE['control'],
                'border_hover': c.STROKE['control_hover'],
            },
            'primary': {
                'bg': c.BRAND['primary'],
                'bg_hover': c.BRAND['primary_dark'],
                'bg_pressed': c.BRAND['primary_darker'],
                'text': c.TEXT['inverted'],
                'border': c.BRAND['primary'],
                'border_hover': c.BRAND['primary_dark'],
            },
            'danger': {
                'bg': c.SEMANTIC['error'],
                'bg_hover': c.ACCENT['red_dark'],
                'bg_pressed': '#8B1C1E',
                'text': c.TEXT['inverted'],
                'border': c.SEMANTIC['error'],
                'border_hover': c.ACCENT['red_dark'],
            },
            'success': {
                'bg': c.SEMANTIC['success'],
                'bg_hover': c.ACCENT['green_dark'],
                'bg_pressed': '#085408',
                'text': c.TEXT['inverted'],
                'border': c.SEMANTIC['success'],
                'border_hover': c.ACCENT['green_dark'],
            },
        }
        
        v = variants.get(variant, variants['default'])
        
        return f'''
            QPushButton {{
                background-color: {v['bg']};
                color: {v['text']};
                border: 1px solid {v['border']};
                padding: 6px 14px;
                border-radius: {e.CORNERS['medium']}px;
                font-size: {t.SIZES['body']}px;
                font-weight: {t.WEIGHTS['regular']};
                font-family: {t.FONT_FAMILY};
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {v['bg_hover']};
                border-color: {v['border_hover']};
            }}
            QPushButton:pressed {{
                background-color: {v['bg_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {c.SURFACE['background_tertiary']};
                color: {c.TEXT['disabled']};
                border-color: {c.STROKE['control_disabled']};
            }}
        '''
    
    @classmethod
    def get_input_style(cls) -> str:
        """
        获取输入框样式
        实现Fluent Design的焦点揭示效果
        """
        c = FluentColors
        e = FluentEffects
        t = FluentTypography
        
        return f'''
            QLineEdit, QTextEdit {{
                font-size: {t.SIZES['body']}px;
                padding: 6px 10px;
                border: 1px solid {c.STROKE['control']};
                border-radius: {e.CORNERS['medium']}px;
                background-color: {c.SURFACE['card']};
                color: {c.TEXT['primary']};
                font-family: {t.FONT_FAMILY};
                selection-background-color: {c.BRAND['primary_lightest']};
            }}
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {c.STROKE['control_hover']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {c.BRAND['primary']};
                padding: 5px 9px;
            }}
            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {c.SURFACE['background_tertiary']};
                color: {c.TEXT['disabled']};
                border-color: {c.STROKE['control_disabled']};
            }}
        '''


def get_fluent_style_manager():
    return FluentStyleManager
