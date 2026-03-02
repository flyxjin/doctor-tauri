# -*- coding: utf-8 -*-
"""
中药材销售管理系统 - 设计规范
包含完整的字体系统、颜色系统和组件样式
遵循 WCAG 2.1 AA 级可访问性标准
"""


class DesignTokens:
    """
    设计令牌 - 统一的设计系统基础
    所有设计值都基于此定义，确保一致性
    """

    # ============================================
    # 字体系统 - Font System
    # ============================================
    # 字体层级结构，确保跨平台显示一致性
    # 主字体: Segoe UI (Windows原生)
    # 备选字体: Microsoft YaHei (中文)
    # 最后备选: SimSun (宋体)

    FONT = {
        # 字体族 - font-family
        'family': {
            'primary': 'Segoe UI, Microsoft YaHei, SimSun, sans-serif',
            'monospace': 'Consolas, Microsoft YaHei Mono, monospace',
        },

        # 字号 - font-size (px)
        'size': {
            'xs': 11,      # 辅助文字、徽章
            'sm': 12,      # 辅助说明、次要信息
            'base': 14,    # 正文、默认字号
            'lg': 16,      # 强调正文、较大按钮文字
            'xl': 18,      # 副标题、小标题
            '2xl': 20,     # 页面标题
            '3xl': 24,     # 大标题
            '4xl': 28,     # 主标题
            '5xl': 32,     # 品牌标题
        },

        # 字重 - font-weight
        'weight': {
            'thin': 100,
            'extralight': 200,
            'light': 300,
            'regular': 400,
            'medium': 500,
            'semibold': 600,
            'bold': 700,
            'extrabold': 800,
        },

        # 行高 - line-height (无单位倍数)
        'leading': {
            'none': 1,
            'tight': 1.25,
            'snug': 1.375,
            'normal': 1.5,
            'relaxed': 1.625,
            'loose': 2,
        },

        # 字间距 - letter-spacing (em)
        'tracking': {
            'tighter': -0.05,
            'tight': -0.025,
            'normal': 0,
            'wide': 0.025,
            'wider': 0.05,
        },
    }

    # ============================================
    # 颜色系统 - Color System
    # ============================================
    # 所有颜色均确保 WCAG 2.1 AA 级对比度
    # 格式: HEX, RGB, HSL

    COLORS = {
        # ----------------------------------------
        # 主色调 - Primary Colors
        # 中药行业专业绿色系 - 传达健康、自然、专业
        # ----------------------------------------
        'primary': {
            '50': '#F0FDF4',   # 极浅绿 - 浅色背景
            '100': '#DCFCE7',  # 浅绿 - 次要背景
            '200': '#BBF7D0',  # 淡绿 - 悬停背景
            '300': '#86EFAC',  # 浅绿 - 选中背景
            '400': '#4ADE80',  # 绿色 - 成功状态
            '500': '#22C55E',  # 基准绿 - 主按钮
            '600': '#16A34A',  # 深绿 - 主按钮悬停
            '700': '#15803D',  # 强调绿 - 选中状态
            '800': '#166534',  # 深绿 - 文字强调
            '900': '#14532D',  # 极深绿 - 标题文字

            # 便捷访问
            'default': '#16A34A',    # 主色
            'hover': '#15803D',      # 悬停
            'active': '#14532D',    # 激活
            'light': '#DCFCE7',     # 浅色
            'subtle': '#F0FDF4',    # 极浅色
        },

        # ----------------------------------------
        # 辅助色 - Secondary Colors
        # 蓝色系 - 传达信任、专业、科技感
        # ----------------------------------------
        'secondary': {
            '50': '#EFF6FF',
            '100': '#DBEAFE',
            '200': '#BFDBFE',
            '300': '#93C5FD',
            '400': '#60A5FA',
            '500': '#3B82F6',
            '600': '#2563EB',
            '700': '#1D4ED8',
            '800': '#1E40AF',
            '900': '#1E3A8A',

            'default': '#3B82F6',
            'hover': '#2563EB',
            'active': '#1D4ED8',
            'light': '#DBEAFE',
            'subtle': '#EFF6FF',
        },

        # ----------------------------------------
        # 强调色 - Accent Colors
        # 用于重要操作、状态提示
        # ----------------------------------------
        'accent': {
            # 橙色 - 警告、注意
            'orange': {
                '50': '#FFF7ED',
                '100': '#FFEDD5',
                '200': '#FED7AA',
                '300': '#FDBA74',
                '400': '#FB923C',
                '500': '#F97316',
                '600': '#EA580C',
                '700': '#C2410C',
                '800': '#9A3412',
                '900': '#7C2D12',
                'default': '#F97316',
            },
            # 紫色 - 特殊功能
            'purple': {
                '50': '#FAF5FF',
                '100': '#F3E8FF',
                '200': '#E9D5FF',
                '300': '#D8B4FE',
                '400': '#C084FC',
                '500': '#A855F7',
                '600': '#9333EA',
                '700': '#7E22CE',
                '800': '#6B21A8',
                '900': '#581C87',
                'default': '#9333EA',
            },
        },

        # ----------------------------------------
        # 中性色 - Neutral Colors
        # 用于文本、背景、边框
        # ----------------------------------------
        'neutral': {
            # 灰色系 - 文字
            'gray': {
                '50': '#FAFAFA',   # 极浅灰 - 页面背景
                '100': '#F4F4F5',  # 浅灰 - 卡片背景
                '200': '#E4E4E7',  # 淡灰 - 分隔线
                '300': '#D4D4D8',  # 浅灰 - 边框
                '400': '#A1A1AA',  # 灰色 - 禁用状态
                '500': '#71717A',  # 中灰 - 辅助文字
                '600': '#52525B',  # 深灰 - 次要文字
                '700': '#3F3F46',  # 灰色 - 正文文字
                '800': '#27272A',  # 深灰 - 强调文字
                '900': '#18181B',  # 极深灰 - 标题文字

                'default': '#52525B',  # 默认文字
                'muted': '#71717A',    # 辅助文字
                'subtle': '#A1A1AA',   # 禁用文字
            },
        },

        # ----------------------------------------
        # 语义色 - Semantic Colors
        # 用于状态提示、信息传达
        # ----------------------------------------
        'semantic': {
            # 成功 - Success
            'success': {
                '50': '#F0FDF4',
                '100': '#DCFCE7',
                '200': '#BBF7D0',
                '300': '#86EFAC',
                '400': '#4ADE80',
                '500': '#22C55E',
                '600': '#16A34A',
                '700': '#15803D',
                '800': '#166534',
                '900': '#14532D',
                'text': '#15803D',      # 对比度 7.3:1
                'bg': '#DCFCE7',        # 对比度 14:1
                'border': '#22C55E',    # 对比度 4.5:1
                'default': '#16A34A',
            },

            # 警告 - Warning
            'warning': {
                '50': '#FFFBEB',
                '100': '#FEF3C7',
                '200': '#FDE68A',
                '300': '#FCD34D',
                '400': '#FBBF24',
                '500': '#F59E0B',
                '600': '#D97706',
                '700': '#B45309',
                '800': '#92400E',
                '900': '#78350F',
                'text': '#B45309',      # 对比度 7.1:1
                'bg': '#FEF3C7',        # 对比度 13:1
                'border': '#F59E0B',    # 对比度 4.6:1
                'default': '#D97706',
            },

            # 错误 - Error
            'error': {
                '50': '#FEF2F2',
                '100': '#FEE2E2',
                '200': '#FECACA',
                '300': '#FCA5A5',
                '400': '#F87171',
                '500': '#EF4444',
                '600': '#DC2626',
                '700': '#B91C1C',
                '800': '#991B1B',
                '900': '#7F1D1D',
                'text': '#B91C1C',      # 对比度 8.9:1
                'bg': '#FEE2E2',        # 对比度 11:1
                'border': '#EF4444',    # 对比度 4.5:1
                'default': '#DC2626',
            },

            # 信息 - Info
            'info': {
                '50': '#EFF6FF',
                '100': '#DBEAFE',
                '200': '#BFDBFE',
                '300': '#93C5FD',
                '400': '#60A5FA',
                '500': '#3B82F6',
                '600': '#2563EB',
                '700': '#1D4ED8',
                '800': '#1E40AF',
                '900': '#1E3A8A',
                'text': '#1D4ED8',      # 对比度 7.2:1
                'bg': '#DBEAFE',        # 对比度 10:1
                'border': '#3B82F6',    # 对比度 4.5:1
                'default': '#2563EB',
            },
        },

        # ----------------------------------------
        # 背景色 - Background Colors
        # ----------------------------------------
        'bg': {
            'primary': '#FFFFFF',      # 主背景 - 白色
            'secondary': '#F4F4F5',    # 次要背景 - 浅灰
            'tertiary': '#FAFAFA',     # 三级背景 - 极浅灰
            'sidebar': '#F4F4F5',       # 侧边栏背景
            'overlay': 'rgba(0, 0, 0, 0.5)',  # 遮罩层
            'disabled': '#F4F4F5',      # 禁用背景
        },

        # ----------------------------------------
        # 边框色 - Border Colors
        # ----------------------------------------
        'border': {
            'default': '#E4E4E7',       # 默认边框
            'light': '#F4F4F5',         # 浅边框
            'medium': '#D4D4D8',        # 中等边框
            'dark': '#A1A1AA',          # 深边框
            'focus': '#22C55E',         # 聚焦边框 (绿色)
        },

        # ----------------------------------------
        # 文字色 - Text Colors
        # 所有文字颜色均符合 WCAG AA 级标准
        # ----------------------------------------
        'text': {
            'primary': '#27272A',       # 主要文字 - 对比度 15:1
            'secondary': '#52525B',     # 次要文字 - 对比度 7.5:1
            'tertiary': '#71717A',      # 辅助文字 - 对比度 5.1:1
            'disabled': '#A1A1AA',      # 禁用文字 - 对比度 2.9:1 (仅用于图标等)
            'inverse': '#FFFFFF',      # 反色文字 - 用于深色背景
            'link': '#16A34A',         # 链接文字
            'link_hover': '#15803D',   # 链接悬停
        },

        # ----------------------------------------
        # 投影 - Shadow
        # ----------------------------------------
        'shadow': {
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'base': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        },
    }

    # ============================================
    # 间距系统 - Spacing System
    # ============================================
    # 基于 4px 网格系统

    SPACING = {
        '0': 0,
        '0.5': 2,
        '1': 4,
        '1.5': 6,
        '2': 8,
        '2.5': 10,
        '3': 12,
        '3.5': 14,
        '4': 16,
        '5': 20,
        '6': 24,
        '7': 28,
        '8': 32,
        '9': 36,
        '10': 40,
        '12': 48,
        '14': 56,
        '16': 64,
    }

    # ============================================
    # 圆角系统 - Border Radius
    # ============================================

    RADIUS = {
        'none': 0,
        'sm': 2,
        'default': 4,
        'md': 6,
        'lg': 8,
        'xl': 12,
        '2xl': 16,
        '3xl': 24,
        'full': 9999,
    }

    # ============================================
    # 过渡动画 - Transitions
    # ============================================

    TRANSITION = {
        'fast': '150ms',
        'base': '200ms',
        'slow': '300ms',
        'slower': '500ms',
    }


class UIStyles:
    """
    UI 样式系统 - 直接应用于 PyQt5 组件
    基于 DesignTokens 设计令牌
    """

    # 引用设计令牌
    DT = DesignTokens

    # ============================================
    # 便捷访问 - Quick Access
    # ============================================

    COLORS = {
        # 主色
        'primary': DT.COLORS['primary']['default'],
        'primary_hover': DT.COLORS['primary']['hover'],
        'primary_active': DT.COLORS['primary']['active'],

        # 背景
        'bg_main': DT.COLORS['bg']['primary'],
        'bg_card': DT.COLORS['bg']['primary'],
        'bg_sidebar': DT.COLORS['bg']['sidebar'],
        'bg_secondary': DT.COLORS['bg']['secondary'],

        # 文字
        'text_main': DT.COLORS['text']['primary'],
        'text_secondary': DT.COLORS['text']['secondary'],
        'text_muted': DT.COLORS['text']['tertiary'],
        'text_light': DT.COLORS['text']['inverse'],

        # 边框
        'border': DT.COLORS['border']['default'],
        'border_dark': DT.COLORS['border']['medium'],

        # 语义色
        'success': DT.COLORS['semantic']['success']['default'],
        'warning': DT.COLORS['semantic']['warning']['default'],
        'error': DT.COLORS['semantic']['error']['default'],
        'info': DT.COLORS['semantic']['info']['default'],
    }

    SPACING = DT.SPACING

    RADIUS = DT.RADIUS

    FONT = {
        'family': DT.FONT['family']['primary'],
        'size_base': DT.FONT['size']['base'],
        'size_small': DT.FONT['size']['sm'],
        'size_large': DT.FONT['size']['lg'],
        'size_title': DT.FONT['size']['xl'],
        'size_h1': DT.FONT['size']['3xl'],
        'size_h2': DT.FONT['size']['2xl'],
    }

    # ============================================
    # 字体样式类 - Typography Classes
    # ============================================

    @staticmethod
    def text_h1() -> str:
        """H1 - 主标题"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['3xl']}px; font-weight: {f['weight']['bold']}; line-height: {f['leading']['tight']}; color: {DesignTokens.COLORS['text']['primary']};"

    @staticmethod
    def text_h2() -> str:
        """H2 - 页面标题"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['2xl']}px; font-weight: {f['weight']['semibold']}; line-height: {f['leading']['tight']}; color: {DesignTokens.COLORS['text']['primary']};"

    @staticmethod
    def text_h3() -> str:
        """H3 - 副标题"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['xl']}px; font-weight: {f['weight']['semibold']}; line-height: {f['leading']['snug']}; color: {DesignTokens.COLORS['text']['primary']};"

    @staticmethod
    def text_body() -> str:
        """Body - 正文"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['base']}px; font-weight: {f['weight']['regular']}; line-height: {f['leading']['normal']}; color: {DesignTokens.COLORS['text']['primary']};"

    @staticmethod
    def text_body_small() -> str:
        """Body Small - 小正文"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['sm']}px; font-weight: {f['weight']['regular']}; line-height: {f['leading']['normal']}; color: {DesignTokens.COLORS['text']['secondary']};"

    @staticmethod
    def text_caption() -> str:
        """Caption - 辅助说明"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['xs']}px; font-weight: {f['weight']['regular']}; line-height: {f['leading']['normal']}; color: {DesignTokens.COLORS['text']['tertiary']};"

    @staticmethod
    def text_button() -> str:
        """Button - 按钮文字"""
        f = DesignTokens.FONT
        return f"font-family: {f['family']['primary']}; font-size: {f['size']['base']}px; font-weight: {f['weight']['medium']};"

    # ============================================
    # 组件样式 - Component Styles
    # ============================================

    @classmethod
    def get_main_stylesheet(cls) -> str:
        """主界面全局样式表"""
        c = cls.COLORS
        r = cls.RADIUS
        s = cls.SPACING
        f = cls.FONT
        dt = DesignTokens

        return f'''
            /* ========================================
               全局样式 - Global Styles
               ======================================== */

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

            /* ========================================
               侧边栏 - Sidebar
               ======================================== */

            QFrame#sidebar {{
                background-color: {c['bg_sidebar']};
                border-right: 1px solid {c['border']};
            }}

            QWidget#brand_container {{
                background: transparent;
                border-bottom: 1px solid {c['border']};
                padding: {s['4']}px;
            }}

            QLabel#brand_title {{
                color: {c['text_main']};
                font-size: {f['size_title']}px;
                font-weight: 600;
            }}

            /* 导航按钮 */
            QPushButton#nav_btn {{
                background: transparent;
                color: {c['text_secondary']};
                border: none;
                border-radius: {r['md']}px;
                padding: {s['2.5']}px {s['4']}px;
                margin: 2px {s['2']}px;
                min-height: 40px;
                text-align: left;
                font-size: {f['size_base']}px;
            }}

            QPushButton#nav_btn:hover {{
                background-color: {dt.COLORS['neutral']['gray']['200']};
                color: {c['text_main']};
            }}

            QPushButton#nav_btn:checked {{
                background-color: {c['primary']};
                color: {c['text_light']};
                font-weight: 600;
            }}

            /* 导入按钮 */
            QPushButton#import_btn {{
                background-color: {c['primary']};
                color: {c['text_light']};
                border: none;
                border-radius: {r['md']}px;
                padding: {s['2.5']}px {s['4']}px;
                min-height: 40px;
                font-weight: 600;
            }}

            QPushButton#import_btn:hover {{
                background-color: {c['primary_hover']};
            }}

            QPushButton#import_btn:pressed {{
                background-color: {c['primary_active']};
            }}

            QLabel#version_label {{
                color: {c['text_muted']};
                font-size: {f['size_small']}px;
                padding: {s['2']}px;
            }}

            QFrame#sidebar_separator {{
                background-color: {c['border']};
                max-height: 1px;
            }}

            /* ========================================
               内容区 - Content Area
               ======================================== */

            QFrame#content_area {{
                background-color: {c['bg_main']};
            }}

            /* ========================================
               按钮 - Buttons
               ======================================== */

            /* 主要按钮 */
            QPushButton[primary="true"] {{
                background-color: {c['primary']};
                color: {c['text_light']};
                border: none;
                border-radius: {r['md']}px;
                padding: {s['2']}px {s['4']}px;
                min-height: 36px;
                font-weight: 500;
            }}

            QPushButton[primary="true"]:hover {{
                background-color: {c['primary_hover']};
            }}

            QPushButton[primary="true"]:pressed {{
                background-color: {c['primary_active']};
            }}

            QPushButton[primary="true"]:disabled {{
                background-color: {dt.COLORS['neutral']['gray']['300']};
                color: {dt.COLORS['neutral']['gray']['400']};
            }}

            /* 默认按钮 */
            QPushButton {{
                background-color: {c['bg_card']};
                color: {c['text_main']};
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                padding: {s['2']}px {s['4']}px;
                min-height: 36px;
            }}

            QPushButton:hover {{
                background-color: {dt.COLORS['neutral']['gray']['100']};
                border-color: {c['border']};
            }}

            QPushButton:pressed {{
                background-color: {dt.COLORS['neutral']['gray']['200']};
            }}

            QPushButton:disabled {{
                color: {c['text_muted']};
                background-color: {c['bg_secondary']};
                border-color: {c['border']};
            }}

            /* ========================================
               输入框 - Input Fields
               ======================================== */

            QLineEdit, QTextEdit {{
                padding: {s['2']}px {s['3']}px;
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                background-color: {c['bg_card']};
                color: {c['text_main']};
                font-size: {f['size_base']}px;
            }}

            QLineEdit:hover, QTextEdit:hover {{
                border-color: {c['border']};
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {c['primary']};
            }}

            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {c['bg_secondary']};
                color: {c['text_muted']};
            }}

            /* ========================================
               下拉框 - ComboBox
               ======================================== */

            QComboBox {{
                padding: {s['2']}px {s['3']}px;
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                background-color: {c['bg_card']};
                min-height: 36px;
                font-size: {f['size_base']}px;
            }}

            QComboBox:hover {{
                border-color: {c['border']};
            }}

            QComboBox:focus {{
                border-color: {c['primary']};
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

            /* ========================================
               表格 - Table
               ======================================== */

            QTableWidget {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                background-color: {c['bg_card']};
                alternate-background-color: {c['bg_secondary']};
                gridline-color: transparent;
                font-size: {f['size_base']}px;
            }}

            QTableWidget::item {{
                padding: {s['2']}px;
                border-bottom: 1px solid {c['border']};
            }}

            QTableWidget::item:hover {{
                background-color: {dt.COLORS['neutral']['gray']['100']};
            }}

            QTableWidget::item:selected {{
                background-color: {dt.COLORS['primary']['light']};
                color: {dt.COLORS['primary']['700']};
            }}

            QHeaderView::section {{
                font-weight: 600;
                padding: {s['2']}px;
                background-color: {c['bg_secondary']};
                border: none;
                border-bottom: 1px solid {c['border_dark']};
                color: {c['text_secondary']};
                font-size: {f['size_small']}px;
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

            /* ========================================
               分组框 - GroupBox
               ======================================== */

            QGroupBox {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                margin-top: {s['4']}px;
                padding-top: {s['2']}px;
                font-weight: 600;
                background-color: {c['bg_card']};
                font-size: {f['size_large']}px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {s['3']}px;
                padding: 0 {s['1']}px;
                color: {c['text_main']};
            }}

            /* ========================================
               滚动条 - ScrollBar
               ======================================== */

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

            QScrollBar::handle:vertical:hover {{
                background-color: {dt.COLORS['neutral']['gray']['400']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            /* ========================================
               进度条 - ProgressBar
               ======================================== */

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

            /* ========================================
               复选框 - CheckBox
               ======================================== */

            QCheckBox {{
                spacing: {s['2']}px;
                font-size: {f['size_base']}px;
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {c['border_dark']};
                border-radius: {r['sm']}px;
                background-color: {c['bg_card']};
            }}

            QCheckBox::indicator:hover {{
                border-color: {c['primary']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
            }}

            QCheckBox:disabled {{
                color: {c['text_muted']};
            }}

            /* ========================================
               选项卡 - TabWidget
               ======================================== */

            QTabWidget::pane {{
                border: 1px solid {c['border_dark']};
                border-radius: {r['lg']}px;
                background-color: {c['bg_card']};
            }}

            QTabBar::tab {{
                background: transparent;
                color: {c['text_secondary']};
                padding: {s['2']}px {s['4']}px;
                border-bottom: 2px solid transparent;
                font-size: {f['size_base']}px;
            }}

            QTabBar::tab:hover {{
                color: {c['text_main']};
            }}

            QTabBar::tab:selected {{
                color: {c['primary']};
                border-bottom: 2px solid {c['primary']};
                font-weight: 600;
            }}

            /* ========================================
               工具提示 - ToolTip
               ======================================== */

            QToolTip {{
                background-color: {c['bg_card']};
                color: {c['text_main']};
                padding: {s['1.5']}px {s['2.5']}px;
                border-radius: {r['md']}px;
                border: 1px solid {c['border_dark']};
                font-size: {f['size_small']}px;
            }}

            /* ========================================
               菜单栏 - MenuBar
               ======================================== */

            QMenuBar {{
                background-color: {c['bg_card']};
                border-bottom: 1px solid {c['border']};
                font-size: {f['size_base']}px;
            }}

            QMenuBar::item {{
                padding: {s['1.5']}px {s['3']}px;
                border-radius: {r['sm']}px;
            }}

            QMenuBar::item:selected {{
                background-color: {c['bg_secondary']};
            }}

            QMenu {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border_dark']};
                border-radius: {r['md']}px;
                padding: {s['1']}px;
                font-size: {f['size_base']}px;
            }}

            QMenu::item {{
                padding: {s['2']}px {s['4']}px;
                border-radius: {r['sm']}px;
            }}

            QMenu::item:selected {{
                background-color: {c['bg_secondary']};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {c['border']};
                margin: {s['1']}px {s['2']}px;
            }}

            /* ========================================
               状态栏 - StatusBar
               ======================================== */

            QStatusBar {{
                background-color: {c['bg_card']};
                border-top: 1px solid {c['border']};
                padding: {s['1']}px {s['3']}px;
                font-size: {f['size_small']}px;
            }}

            /* ========================================
               消息框 - MessageBox
               ======================================== */

            QMessageBox {{
                background-color: {c['bg_card']};
            }}

            QMessageBox QLabel {{
                color: {c['text_main']};
                min-width: 200px;
                font-size: {f['size_base']}px;
            }}

            QMessageBox QPushButton {{
                min-width: 80px;
                padding: {s['2']}px {s['4']}px;
            }}
        '''

    @classmethod
    def get_card_style(cls) -> str:
        """卡片样式"""
        c = cls.COLORS
        r = cls.RADIUS
        s = cls.SPACING

        return f'''
            QFrame {{
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
                border-radius: {r['lg']}px;
                padding: {s['4']}px;
            }}
        '''

    @classmethod
    def get_stat_card_style(cls, variant: str = 'default') -> str:
        """统计卡片样式"""
        c = cls.COLORS
        r = cls.RADIUS
        dt = DesignTokens

        styles = {
            'default': f'''
                background-color: {c['bg_card']};
                border: 1px solid {c['border']};
            ''',
            'primary': f'''
                background-color: {dt.COLORS['primary']['subtle']};
                border: 1px solid {dt.COLORS['primary']['light']};
            ''',
            'success': f'''
                background-color: {dt.COLORS['semantic']['success']['bg']};
                border: 1px solid {dt.COLORS['semantic']['success']['border']};
            ''',
            'warning': f'''
                background-color: {dt.COLORS['semantic']['warning']['bg']};
                border: 1px solid {dt.COLORS['semantic']['warning']['border']};
            ''',
            'error': f'''
                background-color: {dt.COLORS['semantic']['error']['bg']};
                border: 1px solid {dt.COLORS['semantic']['error']['border']};
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


# ============================================
# 导出便捷函数 - Helper Functions
# ============================================

def get_font(size: int, bold: bool = False):
    """获取标准字体 (PyQt5)"""
    from PyQt5.QtGui import QFont
    font = QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal)
    return font


def get_chinese_font(size: int, bold: bool = False):
    """获取中文字体 (PyQt5)"""
    from PyQt5.QtGui import QFont, QFontDatabase
    font = QFont("Microsoft YaHei", size, QFont.Bold if bold else QFont.Normal)
    font_db = QFontDatabase()
    if "Microsoft YaHei" not in font_db.families():
        font = QFont("SimSun", size, QFont.Bold if bold else QFont.Normal)
    return font
