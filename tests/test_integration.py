# tests/test_integration.py
import pytest
from unittest.mock import Mock
from src.models import AgentState, StatusType
from src.state.manager import StateManager
from src.notifier.dispatcher import Dispatcher
from src.notifier.base import BaseNotifier
from datetime import datetime
import asyncio


class MockNotifier(BaseNotifier):
    """模拟通知器"""

    def __init__(self):
        self.sent_states = []

    async def send(self, state: AgentState) -> bool:
        self.sent_states.append(state)
        return True

    def is_available(self) -> bool:
        return True


def test_full_state_flow():
    """测试完整状态流转"""
    manager = StateManager()
    states_received = []
    manager.on_state_change(lambda s: states_received.append(s))

    # 初始状态：等待中
    state1 = AgentState(
        status=StatusType.WAITING,
        task="初始化",
        progress=0,
        message="等待开始",
        started_at=datetime.now()
    )
    manager.update_state(state1)

    # 运行中
    state2 = AgentState(
        status=StatusType.RUNNING,
        task="执行任务",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )
    manager.update_state(state2)

    # 完成
    state3 = AgentState(
        status=StatusType.COMPLETED,
        task="执行任务",
        progress=100,
        message="已完成",
        started_at=datetime.now()
    )
    manager.update_state(state3)

    assert len(states_received) == 3
    assert states_received[0].status == StatusType.WAITING
    assert states_received[1].status == StatusType.RUNNING
    assert states_received[2].status == StatusType.COMPLETED


def test_dispatcher_integration():
    """测试分发器集成"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)

    state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    asyncio.run(dispatcher.dispatch(state))

    assert len(notifier.sent_states) == 1
    assert notifier.sent_states[0].status == StatusType.RUNNING


def test_error_recovery():
    """测试错误恢复"""
    manager = StateManager()
    states_received = []
    manager.on_state_change(lambda s: states_received.append(s))

    # 错误状态
    error_state = AgentState(
        status=StatusType.ERROR,
        task="失败任务",
        progress=30,
        message="出错了",
        started_at=datetime.now(),
        error="连接超时"
    )
    manager.update_state(error_state)

    # 恢复运行
    recovery_state = AgentState(
        status=StatusType.RUNNING,
        task="重试任务",
        progress=0,
        message="重新开始",
        started_at=datetime.now()
    )
    manager.update_state(recovery_state)

    assert len(states_received) == 2
    assert states_received[0].error == "连接超时"
    assert states_received[1].error is None
