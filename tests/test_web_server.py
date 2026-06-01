import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.notifier.web_server import WebNotifier
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


def test_web_notifier_creation():
    """测试创建 Web 通知器"""
    notifier = WebNotifier(port=8080, host="0.0.0.0")
    assert notifier.port == 8080
    assert notifier.host == "0.0.0.0"


def test_web_notifier_is_available():
    """测试可用性检查"""
    notifier = WebNotifier(port=8080)
    assert notifier.is_available() is False


def test_web_notifier_build_message(sample_state):
    """测试构建消息"""
    message = sample_state.to_dict()

    assert message["status"] == "running"
    assert message["task"] == "测试"
    assert message["progress"] == 50


@pytest.mark.asyncio
async def test_web_notifier_broadcast(sample_state):
    """测试广播消息"""
    notifier = WebNotifier(port=8080)

    # 模拟 WebSocket 连接
    mock_ws = AsyncMock()
    notifier._clients.add(mock_ws)

    await notifier._broadcast(sample_state)

    mock_ws.send_json.assert_called_once()
