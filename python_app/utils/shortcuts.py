# -*- coding: utf-8 -*-
"""
全局快捷键管理系统

集中定义和注册所有快捷键，避免分散在各 View 中。
快捷键定义与处理逻辑分离，便于维护和文档化。

快捷键清单：
  Ctrl+1~7    切换到对应页面（首页/药材/处方/客户/库存/历史/统计）
  F5          刷新当前页面数据
  Ctrl+F      聚焦当前页面的搜索框
  Ctrl+N      当前页面新增操作（药材/处方等）
  Ctrl+S      保存（处方页面）
  Ctrl+B      打开批量导入对话框
  Ctrl+E      导出数据
  Ctrl+Q      退出程序
  F1          显示关于对话框
"""
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut

# 快捷键定义表（用于文档展示和注册）
SHORTCUT_DEFINITIONS = [
    ('Ctrl+1', '切换到首页概览'),
    ('Ctrl+2', '切换到药材管理'),
    ('Ctrl+3', '切换到开处方'),
    ('Ctrl+4', '切换到客户管理'),
    ('Ctrl+5', '切换到库存管理'),
    ('Ctrl+6', '切换到处方历史'),
    ('Ctrl+7', '切换到销售统计'),
    ('F5', '刷新当前页面'),
    ('Ctrl+F', '搜索'),
    ('Ctrl+N', '新增'),
    ('Ctrl+S', '保存'),
    ('Ctrl+B', '批量导入'),
    ('Ctrl+E', '导出数据'),
    ('Ctrl+Q', '退出程序'),
    ('F1', '关于'),
]


class ShortcutManager(QObject):
    """快捷键管理器

    绑定到 MainWindow，注册所有快捷键并路由到对应处理函数。
    """

    # 快捷键触发的信号，MainWindow 连接到具体处理逻辑
    switch_view_requested = Signal(str)    # view_name
    refresh_requested = Signal()           # 刷新当前页
    search_focus_requested = Signal()      # 聚焦搜索框
    add_requested = Signal()               # 新增操作
    save_requested = Signal()              # 保存操作
    import_requested = Signal()            # 批量导入
    export_requested = Signal()            # 导出
    about_requested = Signal()             # 关于

    def __init__(self, main_window):
        super().__init__(main_window)
        self._main_window = main_window
        self._shortcuts: list[QShortcut] = []
        self._register_all()

    def _register_all(self):
        """注册所有快捷键"""
        bindings = [
            ('Ctrl+1', lambda: self.switch_view_requested.emit('dashboard')),
            ('Ctrl+2', lambda: self.switch_view_requested.emit('medicine')),
            ('Ctrl+3', lambda: self.switch_view_requested.emit('prescription')),
            ('Ctrl+4', lambda: self.switch_view_requested.emit('patient')),
            ('Ctrl+5', lambda: self.switch_view_requested.emit('inventory')),
            ('Ctrl+6', lambda: self.switch_view_requested.emit('history')),
            ('Ctrl+7', lambda: self.switch_view_requested.emit('statistics')),
            ('F5', self.refresh_requested.emit),
            ('Ctrl+F', self.search_focus_requested.emit),
            ('Ctrl+N', self.add_requested.emit),
            ('Ctrl+S', self.save_requested.emit),
            ('Ctrl+B', self.import_requested.emit),
            ('Ctrl+E', self.export_requested.emit),
            ('F1', self.about_requested.emit),
        ]
        for key_seq, handler in bindings:
            shortcut = QShortcut(QKeySequence(key_seq), self._main_window)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)

    def get_current_view_name(self) -> str:
        """获取当前显示的 view 名称"""
        idx = self._main_window.stacked_widget.currentIndex()
        view_names = ['dashboard', 'medicine', 'prescription', 'patient',
                      'inventory', 'history', 'statistics']
        if 0 <= idx < len(view_names):
            return view_names[idx]
        return ''


def get_shortcut_help_text() -> str:
    """返回快捷键帮助文本（用于关于对话框或帮助页面）"""
    lines = ['<h3>快捷键说明</h3><table style="font-size:13px;">']
    for key, desc in SHORTCUT_DEFINITIONS:
        lines.append(f'<tr><td><b>{key}</b></td><td style="padding-left:12px;">{desc}</td></tr>')
    lines.append('</table>')
    return ''.join(lines)
