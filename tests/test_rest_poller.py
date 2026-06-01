# tests/test_rest_poller.py
import pytest
from unittest.mock import Mock, patch
from src.poller.rest_poller import RestPoller
from src.models import StatusType


def test_rest_poller_creation():
    """测试创建 RestPoller"""
    poller = RestPoller(
        url="http://localhost:8080/api/status",
        interval=5
    )
    assert poller.url == "http://localhost:8080/api/status"
    assert poller.interval == 5


@patch('src.poller.rest_poller.requests.get')
def test_poll_success(mock_get):
    """测试成功轮询"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "running",
        "task": "测试任务",
        "progress": 50,
        "message": "处理中",
        "started_at": "2026-06-01T10:00:00"
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    poller = RestPoller(url="http://test.com/api", interval=5)
    state = poller.poll()

    assert state is not None
    assert state.status == StatusType.RUNNING
    assert state.task == "测试任务"


@patch('src.poller.rest_poller.requests.get')
def test_poll_failure(mock_get):
    """测试轮询失败"""
    mock_get.side_effect = Exception("Connection error")

    poller = RestPoller(url="http://test.com/api", interval=5)
    state = poller.poll()

    assert state is None


def test_on_status_change_callback():
    """测试状态变化回调"""
    poller = RestPoller(url="http://test.com/api", interval=5)
    callback = Mock()
    poller.on_status_change(callback)

    assert callback in poller._callbacks
