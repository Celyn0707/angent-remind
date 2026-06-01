import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.notifier.bluetooth import BluetoothNotifier
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )


def test_bluetooth_notifier_creation():
    """测试创建蓝牙通知器"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    assert notifier.device_name == "Test Monitor"


def test_bluetooth_notifier_is_available():
    """测试可用性检查"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    # 蓝牙可用性取决于 bleak 是否安装
    assert isinstance(notifier.is_available(), bool)


def test_bluetooth_notifier_build_data(sample_state):
    """测试构建数据"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    data = notifier._state_to_bytes(sample_state)

    assert b"running" in data
    assert "测试".encode("utf-8") in data
