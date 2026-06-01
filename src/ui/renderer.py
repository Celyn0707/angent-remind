# src/ui/renderer.py
from typing import Optional
from src.models import AgentState, StatusType
from src.ui.floating_window import FloatingWindow
from src.config import Config


class UIRenderer:
    """UI 渲染器"""

    def __init__(self, config: Config):
        self.config = config
        self.floating_window = FloatingWindow()
        self.tray_icon = None

    def initialize(self):
        """初始化 UI"""
        self._setup_tray()
        self.floating_window.show()

    def _setup_tray(self):
        """设置系统托盘"""
        from src.ui.system_tray import SystemTray
        self.tray_icon = SystemTray(self.floating_window)
        self.tray_icon.show()

    def render(self, state: AgentState):
        """渲染状态"""
        self.floating_window.update_state(state)

    def show_notification(self, title: str, message: str):
        """显示通知"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message)

    def shutdown(self):
        """关闭 UI"""
        if self.tray_icon:
            self.tray_icon.hide()
        self.floating_window.close()
