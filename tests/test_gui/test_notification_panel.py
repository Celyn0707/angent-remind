import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.notification_panel import NotificationPanel
from src.config import Config


@pytest.fixture(scope="session")
def app():
    """创建 QApplication"""
    return QApplication([])


@pytest.fixture
def config():
    """创建配置对象"""
    return Config()


@pytest.fixture
def panel(app, config):
    """创建通知面板"""
    return NotificationPanel(config)


def test_panel_creation(panel):
    """测试面板创建"""
    assert panel is not None


def test_panel_has_wechat_section(panel):
    """测试面板有企业微信区域"""
    assert panel._wechat_enabled_input is not None
    assert panel._wechat_webhook_input is not None


def test_panel_has_web_section(panel):
    """测试面板有手机网页区域"""
    assert panel._web_enabled_input is not None
    assert panel._web_port_input is not None


def test_panel_has_bluetooth_section(panel):
    """测试面板有蓝牙区域"""
    assert panel._bluetooth_enabled_input is not None
    assert panel._bluetooth_device_name_input is not None


def test_panel_load_settings(panel, config):
    """测试加载设置"""
    panel.load_settings()
    assert panel._wechat_enabled_input.isChecked() == config.wechat_enabled
    assert panel._web_port_input.value() == config.web_port
