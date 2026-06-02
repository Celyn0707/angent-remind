import pytest
import tempfile
import os
import yaml
from src.config import Config


def test_config_save():
    """测试保存配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "url": "http://test.com/api",
                "poll_interval": 10
            }
        }, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        config.save(temp_path)

        # 重新加载验证
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved = yaml.safe_load(f)

        assert saved["api"]["url"] == "http://test.com/api"
        assert saved["api"]["poll_interval"] == 10
    finally:
        os.unlink(temp_path)


def test_config_update_and_save():
    """测试更新并保存配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "url": "http://old.com/api",
                "poll_interval": 5
            }
        }, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        config.set("api.url", "http://new.com/api")
        config.set("api.poll_interval", 15)
        config.save(temp_path)

        # 重新加载验证
        config2 = Config(temp_path)
        assert config2.api_url == "http://new.com/api"
        assert config2.poll_interval == 15
    finally:
        os.unlink(temp_path)
