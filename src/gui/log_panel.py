from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class LogPanel(QWidget):
    """日志查看面板"""

    LEVEL_COLORS = {
        "INFO": QColor("#60a5fa"),
        "WARNING": QColor("#fbbf24"),
        "ERROR": QColor("#f87171"),
        "DEBUG": QColor("#6c7086")
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_logs = []
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 工具栏
        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel("日志类型:"))
        self._type_filter = QComboBox()
        self._type_filter.addItems(["全部", "运行日志", "错误日志", "状态变化", "通知日志"])
        self._type_filter.currentTextChanged.connect(self._apply_filter)
        toolbar.addWidget(self._type_filter)

        toolbar.addWidget(QLabel("级别:"))
        self._level_filter = QComboBox()
        self._level_filter.addItems(["全部", "INFO", "WARNING", "ERROR", "DEBUG"])
        self._level_filter.currentTextChanged.connect(self._apply_filter)
        toolbar.addWidget(self._level_filter)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索...")
        self._search_input.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self._search_input)

        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        toolbar.addWidget(self._refresh_btn)

        self._clear_btn = QPushButton("清空")
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self._clear_btn.clicked.connect(self._clear_logs)
        toolbar.addWidget(self._clear_btn)

        self._export_btn = QPushButton("导出")
        self._export_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        toolbar.addWidget(self._export_btn)

        layout.addLayout(toolbar)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 日志表格
        self._log_table = QTableWidget()
        self._log_table.setColumnCount(4)
        self._log_table.setHorizontalHeaderLabels(["时间", "类型", "级别", "内容"])
        self._log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._log_table.currentItemChanged.connect(self._show_log_detail)
        self._log_table.setStyleSheet("""
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
        splitter.addWidget(self._log_table)

        # 日志详情
        detail_group = QGroupBox("日志详情")
        detail_layout = QVBoxLayout(detail_group)
        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: none;
                font-family: Consolas, monospace;
            }
        """)
        detail_layout.addWidget(self._detail_text)
        splitter.addWidget(detail_group)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

    def add_log(self, log_entry: dict):
        """添加日志"""
        self._all_logs.append(log_entry)

        row = self._log_table.rowCount()
        self._log_table.insertRow(row)

        # 时间
        time_item = QTableWidgetItem(log_entry.get("timestamp", ""))
        self._log_table.setItem(row, 0, time_item)

        # 类型
        type_item = QTableWidgetItem(log_entry.get("type", ""))
        self._log_table.setItem(row, 1, type_item)

        # 级别
        level = log_entry.get("level", "INFO")
        level_item = QTableWidgetItem(level)
        level_item.setForeground(self.LEVEL_COLORS.get(level, QColor("#cdd6f4")))
        self._log_table.setItem(row, 2, level_item)

        # 内容
        message_item = QTableWidgetItem(log_entry.get("message", ""))
        self._log_table.setItem(row, 3, message_item)

        # 自动滚动到底部
        self._log_table.scrollToBottom()

    def filter_logs(self, log_type: str, level: str):
        """筛选日志"""
        for i in range(self._log_table.rowCount()):
            type_text = self._log_table.item(i, 1).text()
            level_text = self._log_table.item(i, 2).text()

            type_match = log_type == "全部" or type_text == log_type
            level_match = level == "全部" or level_text == level

            self._log_table.setRowHidden(i, not (type_match and level_match))

    def _apply_filter(self):
        """应用筛选"""
        self.filter_logs(
            self._type_filter.currentText(),
            self._level_filter.currentText()
        )

        # 搜索过滤
        search_text = self._search_input.text().lower()
        if search_text:
            for i in range(self._log_table.rowCount()):
                if self._log_table.isRowHidden(i):
                    continue
                content = self._log_table.item(i, 3).text().lower()
                if search_text not in content:
                    self._log_table.setRowHidden(i, True)

    def _show_log_detail(self, current, previous):
        """显示日志详情"""
        if current is None:
            return

        row = current.row()
        time_text = self._log_table.item(row, 0).text()
        type_text = self._log_table.item(row, 1).text()
        level_text = self._log_table.item(row, 2).text()
        message_text = self._log_table.item(row, 3).text()

        detail = f"时间: {time_text}\n"
        detail += f"类型: {type_text}\n"
        detail += f"级别: {level_text}\n"
        detail += f"内容: {message_text}"
        self._detail_text.setText(detail)

    def _clear_logs(self):
        """清空日志"""
        self._all_logs.clear()
        self._log_table.setRowCount(0)
        self._detail_text.clear()
