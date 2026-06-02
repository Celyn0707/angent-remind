import pytest
from PyQt6.QtWidgets import QApplication
from src.gui.config_panel import ConfigPanel
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
    """创建配置面板"""
    return ConfigPanel(config)


def test_panel_creation(panel):
    """测试面板创建"""
    assert panel is not None


def test_panel_has_api_section(panel):
    """测试面板有 API 配置区域"""
    assert panel._api_url_input is not None
    assert panel._poll_interval_input is not None


def test_panel_load_config(panel, config):
    """测试加载配置"""
    panel.load_config()
    assert panel._api_url_input.text() == config.api_url
    assert panel._poll_interval_input.value() == config.poll_interval


def test_panel_save_config(panel):
    """测试保存配置"""
    panel._api_url_input.setText("http://test.com/api")
    panel._poll_interval_input.setValue(10)
    panel.save_config()

    assert panel._config.api_url == "http://test.com/api"
    assert panel._config.poll_interval == 10
