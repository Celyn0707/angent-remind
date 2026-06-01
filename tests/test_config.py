import pytest
import tempfile
import os
import yaml
from src.config import Config


def test_load_default_config():
    """测试加载默认配置"""
    config = Config()
    assert config.api_type == "rest"
    assert config.poll_interval == 5
    assert config.window_opacity == 0.9


def test_load_custom_config():
    """测试加载自定义配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "type": "websocket",
                "poll_interval": 10
            },
            "window": {
                "opacity": 0.8
            }
        }, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.api_type == "websocket"
        assert config.poll_interval == 10
        assert config.window_opacity == 0.8
    finally:
        os.unlink(temp_path)


def test_config_validation():
    """测试配置验证"""
    config = Config()
    assert config.validate() is True


def test_invalid_poll_interval():
    """测试无效轮询间隔"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "poll_interval": -1
            }
        }, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.validate() is False
    finally:
        os.unlink(temp_path)
