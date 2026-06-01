import pytest
from datetime import datetime
from src.models import AgentState, StatusType


def test_status_type_enum():
    """测试状态类型枚举"""
    assert StatusType.RUNNING.value == "running"
    assert StatusType.COMPLETED.value == "completed"
    assert StatusType.ERROR.value == "error"
    assert StatusType.WAITING.value == "waiting"
    assert StatusType.CONFIRM.value == "confirm"


def test_agent_state_creation():
    """测试创建 AgentState"""
    state = AgentState(
        status=StatusType.RUNNING,
        task="分析代码",
        progress=50,
        message="正在处理...",
        started_at=datetime.now()
    )
    assert state.status == StatusType.RUNNING
    assert state.task == "分析代码"
    assert state.progress == 50
    assert state.error is None
    assert state.confirm_required is False


def test_agent_state_to_dict():
    """测试 AgentState 转换为字典"""
    now = datetime.now()
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=75,
        message="处理中",
        started_at=now
    )
    d = state.to_dict()
    assert d["status"] == "running"
    assert d["task"] == "测试任务"
    assert d["progress"] == 75
    assert d["started_at"] == now.isoformat()


def test_agent_state_from_dict():
    """测试从字典创建 AgentState"""
    now = datetime.now()
    data = {
        "status": "error",
        "task": "测试任务",
        "progress": 30,
        "message": "出错了",
        "started_at": now.isoformat(),
        "error": "连接超时",
        "confirm_required": False
    }
    state = AgentState.from_dict(data)
    assert state.status == StatusType.ERROR
    assert state.error == "连接超时"


def test_invalid_status():
    """测试无效状态类型"""
    with pytest.raises(ValueError):
        StatusType("invalid_status")
