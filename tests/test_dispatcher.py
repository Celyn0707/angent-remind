import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.notifier.dispatcher import Dispatcher
from src.notifier.base import BaseNotifier
from src.models import AgentState, StatusType
from datetime import datetime


class MockNotifier(BaseNotifier):
    """模拟通知器"""

    def __init__(self, available: bool = True, send_side_effect=None):
        self.available = available
        self._send_mock = AsyncMock(return_value=True, side_effect=send_side_effect)

    async def send(self, state: AgentState) -> bool:
        return await self._send_mock(state)

    def is_available(self) -> bool:
        return self.available


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )


def test_dispatcher_register():
    """测试注册通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)
    assert notifier in dispatcher._notifiers


def test_dispatcher_unregister():
    """测试注销通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)
    dispatcher.unregister(notifier)
    assert notifier not in dispatcher._notifiers


def test_dispatcher_dispatch(sample_state):
    """测试分发事件"""
    dispatcher = Dispatcher()
    notifier1 = MockNotifier()
    notifier2 = MockNotifier()
    dispatcher.register(notifier1)
    dispatcher.register(notifier2)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier1._send_mock.assert_called_once_with(sample_state)
    notifier2._send_mock.assert_called_once_with(sample_state)


def test_dispatcher_dispatch_skip_unavailable(sample_state):
    """测试跳过不可用的通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier(available=False)
    dispatcher.register(notifier)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier._send_mock.assert_not_called()


def test_dispatcher_dispatch_continue_on_failure(sample_state):
    """测试单个通知器失败不影响其他"""
    dispatcher = Dispatcher()
    notifier1 = MockNotifier(send_side_effect=Exception("发送失败"))
    notifier2 = MockNotifier()
    dispatcher.register(notifier1)
    dispatcher.register(notifier2)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier1._send_mock.assert_called_once()
    notifier2._send_mock.assert_called_once()
