# tests/test_floating_window.py
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.floating_window import FloatingWindow
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def app():
    """创建 QApplication"""
    return QApplication([])


@pytest.fixture
def window(app):
    """创建悬浮窗"""
    return FloatingWindow()


def test_window_creation(window):
    """测试窗口创建"""
    assert window is not None
    assert window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


def test_window_update_state(window):
    """测试更新状态"""
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    window.update_state(state)
    assert window._current_state == state


def test_window_toggle_expand(window):
    """测试展开/收起"""
    assert window._expanded is False

    window.toggle_expand()
    assert window._expanded is True

    window.toggle_expand()
    assert window._expanded is False