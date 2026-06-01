import os
from pathlib import Path
from typing import Optional, List
import yaml


class Config:
    """配置管理类"""

    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default.yaml"

    def __init__(self, config_path: Optional[str] = None):
        self._config = self._load_default()

        if config_path and os.path.exists(config_path):
            user_config = self._load_yaml(config_path)
            self._merge(user_config)

    def _load_yaml(self, path: str) -> dict:
        """加载 YAML 文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _load_default(self) -> dict:
        """加载默认配置"""
        if self.DEFAULT_CONFIG_PATH.exists():
            return self._load_yaml(str(self.DEFAULT_CONFIG_PATH))
        return {}

    def _merge(self, user_config: dict):
        """合并用户配置"""
        for key, value in user_config.items():
            if isinstance(value, dict) and key in self._config:
                self._config[key].update(value)
            else:
                self._config[key] = value

    @property
    def api_type(self) -> str:
        return self._config.get("api", {}).get("type", "rest")

    @property
    def api_url(self) -> str:
        return self._config.get("api", {}).get("url", "")

    @property
    def poll_interval(self) -> int:
        return self._config.get("api", {}).get("poll_interval", 5)

    @property
    def api_timeout(self) -> int:
        return self._config.get("api", {}).get("timeout", 10)

    @property
    def api_headers(self) -> dict:
        return self._config.get("api", {}).get("headers", {})

    @property
    def retry_count(self) -> int:
        return self._config.get("api", {}).get("retry_count", 3)

    @property
    def window_opacity(self) -> float:
        return self._config.get("window", {}).get("opacity", 0.9)

    @property
    def window_position(self) -> str:
        return self._config.get("window", {}).get("position", "bottom-right")

    @property
    def always_on_top(self) -> bool:
        return self._config.get("window", {}).get("always_on_top", True)

    @property
    def colors(self) -> dict:
        return self._config.get("colors", {})

    @property
    def sounds_enabled(self) -> bool:
        return self._config.get("sounds", {}).get("enabled", True)

    @property
    def sound_volume(self) -> float:
        return self._config.get("sounds", {}).get("volume", 0.7)

    # 通知配置属性
    @property
    def wechat_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("wechat", {}).get("enabled", True)

    @property
    def wechat_webhook(self) -> str:
        return self._config.get("notifications", {}).get("wechat", {}).get("webhook", "")

    @property
    def wechat_push_on(self) -> List[str]:
        return self._config.get("notifications", {}).get("wechat", {}).get("push_on", ["running", "completed", "error", "waiting", "confirm"])

    @property
    def web_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("web", {}).get("enabled", True)

    @property
    def web_port(self) -> int:
        return self._config.get("notifications", {}).get("web", {}).get("port", 8080)

    @property
    def web_host(self) -> str:
        return self._config.get("notifications", {}).get("web", {}).get("host", "0.0.0.0")

    @property
    def bluetooth_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("enabled", False)

    @property
    def bluetooth_device_name(self) -> str:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("device_name", "Agent Monitor")

    @property
    def bluetooth_auto_reconnect(self) -> bool:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("auto_reconnect", True)

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.poll_interval <= 0:
            return False
        if self.api_timeout <= 0:
            return False
        if not 0 <= self.window_opacity <= 1:
            return False
        if self.web_port < 0 or self.web_port > 65535:
            return False
        return True
