# src/ui/system_tray.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from src.ui.floating_window import FloatingWindow


class SystemTray(QSystemTrayIcon):
    """系统托盘"""

    def __init__(self, floating_window: FloatingWindow, parent=None):
        super().__init__(parent)
        self.floating_window = floating_window
        self._setup_menu()
        self._setup_icon()

    def _setup_icon(self):
        """设置图标"""
        self.setIcon(QIcon.fromTheme("dialog-information"))
        self.setToolTip("Agent 状态监控")

    def _setup_menu(self):
        """设置菜单"""
        menu = QMenu()

        # 显示/隐藏悬浮窗
        toggle_action = QAction("显示/隐藏悬浮窗", menu)
        toggle_action.triggered.connect(self._toggle_window)
        menu.addAction(toggle_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _toggle_window(self):
        """切换悬浮窗显示"""
        if self.floating_window.isVisible():
            self.floating_window.hide()
        else:
            self.floating_window.show()
