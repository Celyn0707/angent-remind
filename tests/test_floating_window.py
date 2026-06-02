# tests/test_floating_window.py
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.floating_window import FloatingWindow
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture(scope="session")
def app():
    """创建 QApplication（整个测试会话只创建一次）"""
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    yield instance


@pytest.fixture
def window(app):
    """创建悬浮窗"""
    return FloatingWindow()


def test_window_creation(window):
    """测试窗口创建"""
    assert window is not None
    assert window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


def test_window_default_size(window):
    """测试窗口默认尺寸"""
    assert window.width() == 200
    assert window.height() == 80


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


def test_update_state_labels(window):
    """测试更新状态后标签文本正确"""
    state = AgentState(
        status=StatusType.ERROR,
        task="出错任务",
        progress=0,
        message="发生了错误",
        started_at=datetime.now()
    )

    window.update_state(state)
    assert window._icon_label.text() == "❌"
    assert window._status_label.text() == "错误"
    assert window._message_label.text() == "发生了错误"


def test_update_state_long_message_truncated(window):
    """测试长消息被截断"""
    long_msg = "这是一条非常非常长的消息内容超过二十个字符没问题"
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=10,
        message=long_msg,
        started_at=datetime.now()
    )

    window.update_state(state)
    assert window._message_label.text() == long_msg[:20] + "..."
    assert len(window._message_label.text()) == 23  # 20 chars + "..."


def test_update_state_none_is_noop(window):
    """测试传入 None 不会崩溃"""
    window.update_state(None)
    assert window._current_state is None


def test_update_state_invalid_type_is_noop(window):
    """测试传入非 AgentState 对象不会崩溃"""
    window.update_state("not a state")
    assert window._current_state is None


def test_window_toggle_expand(window):
    """测试展开/收起"""
    assert window._expanded is False

    window.toggle_expand()
    assert window._expanded is True
    assert window.width() == 300
    assert window.height() == 200

    window.toggle_expand()
    assert window._expanded is False
    assert window.width() == 200
    assert window.height() == 80
