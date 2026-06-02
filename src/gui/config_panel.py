from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QComboBox, QSlider, QPushButton, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt
from src.config import Config


class ConfigPanel(QWidget):
    """配置管理面板"""

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self.load_config()

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

        # API 配置组
        api_group = QGroupBox("API 配置")
        api_layout = QVBoxLayout(api_group)

        # API 地址
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("API 地址:"))
        self._api_url_input = QLineEdit()
        url_layout.addWidget(self._api_url_input)
        api_layout.addLayout(url_layout)

        # 轮询间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("轮询间隔:"))
        self._poll_interval_input = QSpinBox()
        self._poll_interval_input.setRange(1, 60)
        self._poll_interval_input.setSuffix(" 秒")
        interval_layout.addWidget(self._poll_interval_input)
        interval_layout.addStretch()
        api_layout.addLayout(interval_layout)

        # 超时时间
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("超时时间:"))
        self._api_timeout_input = QSpinBox()
        self._api_timeout_input.setRange(1, 300)
        self._api_timeout_input.setSuffix(" 秒")
        timeout_layout.addWidget(self._api_timeout_input)
        timeout_layout.addStretch()
        api_layout.addLayout(timeout_layout)

        # 重试次数
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("重试次数:"))
        self._retry_count_input = QSpinBox()
        self._retry_count_input.setRange(0, 10)
        retry_layout.addWidget(self._retry_count_input)
        retry_layout.addStretch()
        api_layout.addLayout(retry_layout)

        scroll_layout.addWidget(api_group)

        # 界面配置组
        window_group = QGroupBox("界面配置")
        window_layout = QVBoxLayout(window_group)

        # 悬浮窗位置
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("悬浮窗位置:"))
        self._window_position_input = QComboBox()
        self._window_position_input.addItems([
            "左上角", "右上角", "左下角", "右下角"
        ])
        pos_layout.addWidget(self._window_position_input)
        pos_layout.addStretch()
        window_layout.addLayout(pos_layout)

        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_label = QLabel("90%")
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self._opacity_slider)
        opacity_layout.addWidget(self._opacity_label)
        window_layout.addLayout(opacity_layout)

        # 置顶显示
        self._always_on_top_input = QCheckBox("置顶显示")
        window_layout.addWidget(self._always_on_top_input)

        scroll_layout.addWidget(window_group)

        # 声音配置组
        sound_group = QGroupBox("声音配置")
        sound_layout = QVBoxLayout(sound_group)

        self._sounds_enabled_input = QCheckBox("启用声音")
        sound_layout.addWidget(self._sounds_enabled_input)

        # 音量
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_label = QLabel("70%")
        self._volume_slider.valueChanged.connect(
            lambda v: self._volume_label.setText(f"{v}%")
        )
        volume_layout.addWidget(self._volume_slider)
        volume_layout.addWidget(self._volume_label)
        sound_layout.addLayout(volume_layout)

        scroll_layout.addWidget(sound_group)

        # 日志配置组
        log_group = QGroupBox("日志配置")
        log_layout = QVBoxLayout(log_group)

        self._logging_enabled_input = QCheckBox("启用日志")
        log_layout.addWidget(self._logging_enabled_input)

        # 日志级别
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("日志级别:"))
        self._log_level_input = QComboBox()
        self._log_level_input.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        level_layout.addWidget(self._log_level_input)
        level_layout.addStretch()
        log_layout.addLayout(level_layout)

        scroll_layout.addWidget(log_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._save_btn = QPushButton("保存配置")
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
        self._save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(self._save_btn)

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
        self._reset_btn.clicked.connect(self.load_config)
        btn_layout.addWidget(self._reset_btn)

        layout.addLayout(btn_layout)

    def load_config(self):
        """加载配置"""
        # API 配置
        self._api_url_input.setText(self._config.api_url)
        self._poll_interval_input.setValue(self._config.poll_interval)
        self._api_timeout_input.setValue(self._config.api_timeout)
        self._retry_count_input.setValue(self._config.retry_count)

        # 界面配置
        position_map = {
            "top-left": 0, "top-right": 1,
            "bottom-left": 2, "bottom-right": 3
        }
        self._window_position_input.setCurrentIndex(
            position_map.get(self._config.window_position, 3)
        )
        self._opacity_slider.setValue(int(self._config.window_opacity * 100))
        self._always_on_top_input.setChecked(self._config.always_on_top)

        # 声音配置
        self._sounds_enabled_input.setChecked(self._config.sounds_enabled)
        self._volume_slider.setValue(int(self._config.sound_volume * 100))

        # 日志配置
        self._logging_enabled_input.setChecked(self._config.logging_enabled)
        level_index = self._log_level_input.findText(self._config.log_level)
        if level_index >= 0:
            self._log_level_input.setCurrentIndex(level_index)

    def save_config(self):
        """保存配置"""
        # API 配置
        self._config.set("api.url", self._api_url_input.text())
        self._config.set("api.poll_interval", self._poll_interval_input.value())
        self._config.set("api.timeout", self._api_timeout_input.value())
        self._config.set("api.retry_count", self._retry_count_input.value())

        # 界面配置
        position_map = {0: "top-left", 1: "top-right", 2: "bottom-left", 3: "bottom-right"}
        self._config.set("window.position", position_map[self._window_position_input.currentIndex()])
        self._config.set("window.opacity", self._opacity_slider.value() / 100)
        self._config.set("window.always_on_top", self._always_on_top_input.isChecked())

        # 声音配置
        self._config.set("sounds.enabled", self._sounds_enabled_input.isChecked())
        self._config.set("sounds.volume", self._volume_slider.value() / 100)

        # 日志配置
        self._config.set("logging.enabled", self._logging_enabled_input.isChecked())
        self._config.set("logging.level", self._log_level_input.currentText())

        # 验证配置
        if not self._config.validate():
            QMessageBox.warning(self, "配置错误", "配置验证失败，请检查输入参数是否合法。")
            return

        # 保存到文件
        self._config.save()
