# tests/test_state_manager.py
import pytest
from unittest.mock import Mock
from datetime import datetime
from src.state.manager import StateManager
from src.models import AgentState, StatusType


def test_state_manager_initial_state():
    """测试初始状态"""
    manager = StateManager()
    state = manager.get_current_state()
    assert state is None


def test_state_manager_update():
    """测试更新状态"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    new_state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=0,
        message="开始",
        started_at=datetime.now()
    )

    manager.update_state(new_state)
    assert manager.get_current_state() == new_state
    callback.assert_called_once_with(new_state)


def test_state_manager_history():
    """测试状态历史"""
    manager = StateManager()

    for i in range(5):
        state = AgentState(
            status=StatusType.RUNNING,
            task=f"任务{i}",
            progress=i * 20,
            message=f"进度 {i}",
            started_at=datetime.now()
        )
        manager.update_state(state)

    history = manager.get_history()
    assert len(history) == 5
    assert history[-1].task == "任务4"


def test_state_manager_no_duplicate_notification():
    """测试相同状态不重复通知"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    manager.update_state(state)
    manager.update_state(state)

    assert callback.call_count == 1


def test_state_manager_history_limit():
    """测试历史记录限制"""
    manager = StateManager(max_history=10)

    for i in range(15):
        state = AgentState(
            status=StatusType.RUNNING,
            task=f"任务{i}",
            progress=i,
            message=f"消息{i}",
            started_at=datetime.now()
        )
        manager.update_state(state)

    history = manager.get_history()
    assert len(history) == 10
    assert history[0].task == "任务5"


def test_state_manager_update_none():
    """测试传入 None 时安全忽略而不崩溃"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    manager.update_state(None)

    assert manager.get_current_state() is None
    callback.assert_not_called()


def test_state_manager_update_invalid_type():
    """测试传入非法类型时安全忽略而不崩溃"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    manager.update_state("not a state")
    manager.update_state(123)
    manager.update_state({"status": "running"})

    assert manager.get_current_state() is None
    callback.assert_not_called()
