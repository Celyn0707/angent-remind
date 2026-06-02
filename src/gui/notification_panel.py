from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from src.config import Config


class NotificationPanel(QWidget):
    """通知管理面板"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 企业微信组
        wechat_group = QGroupBox("企业微信")
        wechat_layout = QVBoxLayout(wechat_group)

        self._wechat_enabled_input = QCheckBox("启用企业微信推送")
        wechat_layout.addWidget(self._wechat_enabled_input)

        webhook_layout = QHBoxLayout()
        webhook_layout.addWidget(QLabel("Webhook URL:"))
        self._wechat_webhook_input = QLineEdit()
        self._wechat_webhook_input.setPlaceholderText("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...")
        webhook_layout.addWidget(self._wechat_webhook_input)
        wechat_layout.addLayout(webhook_layout)

        self._test_wechat_btn = QPushButton("测试连接")
        self._test_wechat_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self._test_wechat_btn.clicked.connect(self._on_test_wechat)
        wechat_layout.addWidget(self._test_wechat_btn)

        scroll_layout.addWidget(wechat_group)

        # 手机网页组
        web_group = QGroupBox("手机网页")
        web_layout = QVBoxLayout(web_group)

        self._web_enabled_input = QCheckBox("启用手机网页")
        web_layout.addWidget(self._web_enabled_input)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self._web_port_input = QSpinBox()
        self._web_port_input.setRange(1024, 65535)
        port_layout.addWidget(self._web_port_input)
        port_layout.addStretch()
        web_layout.addLayout(port_layout)

        self._web_url_label = QLabel("访问地址：http://localhost:8080")
        self._web_url_label.setStyleSheet("color: #89b4fa;")
        web_layout.addWidget(self._web_url_label)

        self._web_status_label = QLabel("连接状态：未连接")
        web_layout.addWidget(self._web_status_label)

        scroll_layout.addWidget(web_group)

        # 蓝牙组
        bluetooth_group = QGroupBox("蓝牙连接")
        bluetooth_layout = QVBoxLayout(bluetooth_group)

        self._bluetooth_enabled_input = QCheckBox("启用蓝牙连接")
        bluetooth_layout.addWidget(self._bluetooth_enabled_input)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("设备名称:"))
        self._bluetooth_device_name_input = QLineEdit()
        name_layout.addWidget(self._bluetooth_device_name_input)
        bluetooth_layout.addLayout(name_layout)

        self._bluetooth_auto_reconnect_input = QCheckBox("自动重连")
        bluetooth_layout.addWidget(self._bluetooth_auto_reconnect_input)

        self._bluetooth_status_label = QLabel("连接状态：未连接")
        bluetooth_layout.addWidget(self._bluetooth_status_label)

        btn_layout = QHBoxLayout()
        self._scan_bluetooth_btn = QPushButton("扫描设备")
        self._scan_bluetooth_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self._scan_bluetooth_btn.clicked.connect(self._on_scan_bluetooth)
        btn_layout.addWidget(self._scan_bluetooth_btn)

        self._pair_bluetooth_btn = QPushButton("配对")
        self._pair_bluetooth_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self._pair_bluetooth_btn.clicked.connect(self._on_pair_bluetooth)
        btn_layout.addWidget(self._pair_bluetooth_btn)
        btn_layout.addStretch()
        bluetooth_layout.addLayout(btn_layout)

        scroll_layout.addWidget(bluetooth_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 按钮
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()

        self._save_btn = QPushButton("保存设置")
        self._save_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        self._save_btn.clicked.connect(self.save_settings)
        bottom_btn_layout.addWidget(self._save_btn)

        self._reset_btn = QPushButton("重置")
        self._reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self._reset_btn.clicked.connect(self.load_settings)
        bottom_btn_layout.addWidget(self._reset_btn)

        layout.addLayout(bottom_btn_layout)

    def _on_test_wechat(self):
        """测试企业微信连接"""
        QMessageBox.information(self, "提示", "功能开发中...")

    def _on_scan_bluetooth(self):
        """扫描蓝牙设备"""
        QMessageBox.information(self, "提示", "功能开发中...")

    def _on_pair_bluetooth(self):
        """配对蓝牙设备"""
        QMessageBox.information(self, "提示", "功能开发中...")

    def load_settings(self):
        """加载设置"""
        # 企业微信
        self._wechat_enabled_input.setChecked(self._config.wechat_enabled)
        self._wechat_webhook_input.setText(self._config.wechat_webhook)

        # 手机网页
        self._web_enabled_input.setChecked(self._config.web_enabled)
        self._web_port_input.setValue(self._config.web_port)
        self._web_url_label.setText(f"访问地址：http://localhost:{self._config.web_port}")

        # 蓝牙
        self._bluetooth_enabled_input.setChecked(self._config.bluetooth_enabled)
        self._bluetooth_device_name_input.setText(self._config.bluetooth_device_name)
        self._bluetooth_auto_reconnect_input.setChecked(self._config.bluetooth_auto_reconnect)

    def save_settings(self):
        """保存设置"""
        # 企业微信
        self._config.set("notifications.wechat.enabled", self._wechat_enabled_input.isChecked())
        self._config.set("notifications.wechat.webhook", self._wechat_webhook_input.text())

        # 手机网页
        self._config.set("notifications.web.enabled", self._web_enabled_input.isChecked())
        self._config.set("notifications.web.port", self._web_port_input.value())

        # 蓝牙
        self._config.set("notifications.bluetooth.enabled", self._bluetooth_enabled_input.isChecked())
        self._config.set("notifications.bluetooth.device_name", self._bluetooth_device_name_input.text())
        self._config.set("notifications.bluetooth.auto_reconnect", self._bluetooth_auto_reconnect_input.isChecked())

        # 验证配置
        if not self._config.validate():
            QMessageBox.warning(self, "配置错误", "配置验证失败，请检查输入参数是否合法。")
            return

        # 保存到文件
        self._config.save()
