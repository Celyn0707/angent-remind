# src/ui/floating_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
from typing import Optional
from src.models import AgentState, StatusType


class FloatingWindow(QWidget):
    """悬浮窗"""

    STATUS_COLORS = {
        StatusType.RUNNING: "#4ade80",
        StatusType.COMPLETED: "#60a5fa",
        StatusType.ERROR: "#f87171",
        StatusType.WAITING: "#fbbf24",
        StatusType.CONFIRM: "#c084fc"
    }

    STATUS_ICONS = {
        StatusType.RUNNING: "⚡",
        StatusType.COMPLETED: "✅",
        StatusType.ERROR: "❌",
        StatusType.WAITING: "⏳",
        StatusType.CONFIRM: "❓"
    }

    STATUS_TEXT = {
        StatusType.RUNNING: "运行中",
        StatusType.COMPLETED: "已完成",
        StatusType.ERROR: "错误",
        StatusType.WAITING: "等待中",
        StatusType.CONFIRM: "需要确认"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state: Optional[AgentState] = None
        self._expanded = False
        self._drag_pos: Optional[QPoint] = None

        self._setup_ui()
        self._setup_window()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 80)

        # 默认位置：右下角
        self._move_to_default_position()

    def _move_to_default_position(self):
        """移动到默认位置"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 20
        self.move(x, y)

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # 状态图标和文本
        self._icon_label = QLabel("⏳")
        self._icon_label.setFont(QFont("Segoe UI Emoji", 24))
        layout.addWidget(self._icon_label)

        self._status_label = QLabel("等待中")
        self._status_label.setFont(QFont("Microsoft YaHei", 12))
        layout.addWidget(self._status_label)

        self._message_label = QLabel("点击查看详情")
        self._message_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self._message_label)

        self.setLayout(layout)

    def update_state(self, state: AgentState):
        """更新状态"""
        if state is None or not isinstance(state, AgentState):
            return

        self._current_state = state

        # 更新图标
        icon = self.STATUS_ICONS.get(state.status, "")
        self._icon_label.setText(icon)

        # 更新状态文本
        status_text = self.STATUS_TEXT.get(state.status, "")
        self._status_label.setText(status_text)

        # 更新消息
        message = state.message
        if len(message) > 20:
            message = message[:20] + "..."
        self._message_label.setText(message)

        # 更新背景颜色
        color = self.STATUS_COLORS.get(state.status, "#888888")
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                color: white;
            }}
        """)

    def toggle_expand(self):
        """切换展开/收起"""
        self._expanded = not self._expanded
        if self._expanded:
            self.setFixedSize(300, 200)
        else:
            self.setFixedSize(200, 80)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        self.toggle_expand()
