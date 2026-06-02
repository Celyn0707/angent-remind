import pytest
from datetime import datetime
from src.gui.status_panel import StatusPanel
from src.models import AgentState, StatusType


@pytest.fixture
def panel(app):
    """创建状态面板"""
    return StatusPanel()


def test_panel_creation(panel):
    """测试面板创建"""
    assert panel is not None


def test_panel_update_status(panel):
    """测试更新状态"""
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    panel.update_status(state)
    assert panel._status_label.text() == "运行中"
    assert panel._task_label.text() == "任务：测试任务"
    assert panel._progress_bar.value() == 50


def test_panel_update_history(panel):
    """测试更新历史记录"""
    history = [
        AgentState(
            status=StatusType.RUNNING,
            task="任务1",
            progress=50,
            message="处理中",
            started_at=datetime.now()
        ),
        AgentState(
            status=StatusType.COMPLETED,
            task="任务1",
            progress=100,
            message="完成",
            started_at=datetime.now()
        )
    ]

    panel.update_history(history)
    assert panel._history_table.rowCount() == 2
