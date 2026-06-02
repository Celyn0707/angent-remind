from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from src.models import AgentState, StatusType
from datetime import datetime


class StatusPanel(QWidget):
    """状态监控面板"""

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

    STATUS_COLORS = {
        StatusType.RUNNING: "#4ade80",
        StatusType.COMPLETED: "#60a5fa",
        StatusType.ERROR: "#f87171",
        StatusType.WAITING: "#fbbf24",
        StatusType.CONFIRM: "#c084fc"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._started_at = None
        self._setup_ui()

        # 运行时间定时器
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_runtime)
        self._timer.start(1000)

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 当前状态组
        status_group = QGroupBox("当前状态")
        status_layout = QVBoxLayout(status_group)

        # 状态图标和文本
        self._status_icon = QLabel("⏳")
        self._status_icon.setFont(QFont("Segoe UI Emoji", 48))
        self._status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self._status_icon)

        self._status_label = QLabel("等待中")
        self._status_label.setFont(QFont("Microsoft YaHei", 24))
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self._status_label)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #313244;
                height: 20px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #4ade80;
                border-radius: 10px;
            }
        """)
        status_layout.addWidget(self._progress_bar)

        # 任务信息
        self._task_label = QLabel("任务：-")
        self._task_label.setFont(QFont("Microsoft YaHei", 12))
        status_layout.addWidget(self._task_label)

        self._message_label = QLabel("消息：-")
        self._message_label.setFont(QFont("Microsoft YaHei", 10))
        self._message_label.setStyleSheet("color: #6c7086;")
        status_layout.addWidget(self._message_label)

        self._runtime_label = QLabel("已运行：0 分 0 秒")
        self._runtime_label.setFont(QFont("Microsoft YaHei", 10))
        self._runtime_label.setStyleSheet("color: #6c7086;")
        status_layout.addWidget(self._runtime_label)

        layout.addWidget(status_group)

        # 历史记录组
        history_group = QGroupBox("状态历史")
        history_layout = QVBoxLayout(history_group)

        self._history_table = QTableWidget()
        self._history_table.setColumnCount(4)
        self._history_table.setHorizontalHeaderLabels(["时间", "状态", "任务", "进度"])
        self._history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._history_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: none;
                gridline-color: #313244;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 5px;
            }
        """)
        history_layout.addWidget(self._history_table)

        layout.addWidget(history_group)

    def update_status(self, state: AgentState):
        """更新状态"""
        # 更新图标
        icon = self.STATUS_ICONS.get(state.status, "?")
        self._status_icon.setText(icon)

        # 更新状态文本
        status_text = self.STATUS_TEXT.get(state.status, "未知")
        self._status_label.setText(status_text)

        # 更新颜色
        color = self.STATUS_COLORS.get(state.status, "#888888")
        self._status_label.setStyleSheet(f"color: {color};")
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 10px;
                background-color: #313244;
                height: 20px;
                text-align: center;
                color: #cdd6f4;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 10px;
            }}
        """)

        # 更新进度
        self._progress_bar.setValue(state.progress)

        # 更新任务信息
        self._task_label.setText(f"任务：{state.task}")
        self._message_label.setText(f"消息：{state.message}")

        # 记录开始时间
        self._started_at = state.started_at

    def update_history(self, history: list):
        """更新历史记录"""
        self._history_table.setRowCount(len(history))

        for i, state in enumerate(reversed(history)):
            # 时间
            time_item = QTableWidgetItem(state.started_at.strftime("%H:%M:%S"))
            self._history_table.setItem(i, 0, time_item)

            # 状态
            status_text = self.STATUS_TEXT.get(state.status, "未知")
            icon = self.STATUS_ICONS.get(state.status, "?")
            status_item = QTableWidgetItem(f"{icon} {status_text}")
            self._history_table.setItem(i, 1, status_item)

            # 任务
            task_item = QTableWidgetItem(state.task)
            self._history_table.setItem(i, 2, task_item)

            # 进度
            progress_item = QTableWidgetItem(f"{state.progress}%")
            self._history_table.setItem(i, 3, progress_item)

    def _update_runtime(self):
        """更新运行时间"""
        if self._started_at:
            now = datetime.now()
            diff = (now - self._started_at).total_seconds()
            minutes = int(diff // 60)
            seconds = int(diff % 60)
            self._runtime_label.setText(f"已运行：{minutes} 分 {seconds} 秒")
