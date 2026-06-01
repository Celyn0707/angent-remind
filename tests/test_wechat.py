import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from src.notifier.wechat import WeChatNotifier
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="分析代码",
        progress=50,
        message="正在处理第3个文件",
        started_at=datetime.now()
    )


def test_wechat_notifier_creation():
    """测试创建企业微信通知器"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    assert notifier.webhook == "https://test.webhook.com"


def test_wechat_notifier_no_webhook():
    """测试没有 webhook 时不可用"""
    notifier = WeChatNotifier(webhook="")
    assert notifier.is_available() is False


def test_wechat_notifier_with_webhook():
    """测试有 webhook 时可用"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    assert notifier.is_available() is True


@patch('src.notifier.wechat.requests.post')
def test_wechat_notifier_send(mock_post, sample_state):
    """测试发送通知"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0}
    mock_post.return_value = mock_response

    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    result = asyncio.run(notifier.send(sample_state))

    assert result is True
    mock_post.assert_called_once()


def test_wechat_notifier_build_message(sample_state):
    """测试构建消息"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    message = notifier._build_message(sample_state)

    assert "运行中" in message
    assert "分析代码" in message
    assert "50%" in message
