from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget,
    QStackedWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MainWindow(QMainWindow):
    """管理控制台主窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agent 状态监控 - 管理控制台")
        self.setMinimumSize(900, 600)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        self._sidebar = QListWidget()
        self._sidebar.setFixedWidth(150)
        self._sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-bottom: 1px solid #313244;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
        """)

        # 添加导航项
        items = ["配置管理", "状态监控", "通知管理", "日志查看"]
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._sidebar.addItem(item)

        layout.addWidget(self._sidebar)

        # 内容区域
        self._content_area = QStackedWidget()
        self._content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #181825;
            }
        """)
        layout.addWidget(self._content_area)

        # 添加占位面板（后续任务会替换）
        for i in range(4):
            placeholder = QWidget()
            self._content_area.addWidget(placeholder)

    def _connect_signals(self):
        """连接信号"""
        self._sidebar.currentRowChanged.connect(self._content_area.setCurrentIndex)

    def add_panel(self, panel: QWidget, index: int):
        """添加面板到指定位置"""
        self._content_area.removeWidget(self._content_area.widget(index))
        self._content_area.insertWidget(index, panel)
