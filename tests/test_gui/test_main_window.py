import pytest
from PyQt6.QtCore import Qt
from src.gui.main_window import MainWindow


@pytest.fixture
def window(app):
    """创建主窗口"""
    return MainWindow()


def test_window_creation(window):
    """测试窗口创建"""
    assert window is not None
    assert window.windowTitle() == "Agent 状态监控 - 管理控制台"


def test_window_has_sidebar(window):
    """测试窗口有侧边栏"""
    assert window._sidebar is not None


def test_window_has_content_area(window):
    """测试窗口有内容区域"""
    assert window._content_area is not None


def test_window_sidebar_items(window):
    """测试侧边栏项目"""
    items = []
    for i in range(window._sidebar.count()):
        items.append(window._sidebar.item(i).text())

    assert "配置管理" in items
    assert "状态监控" in items
    assert "通知管理" in items
    assert "日志查看" in items


def test_window_switch_panel(window):
    """测试切换面板"""
    # 点击状态监控
    window._sidebar.setCurrentRow(1)
    assert window._content_area.currentIndex() == 1

    # 点击通知管理
    window._sidebar.setCurrentRow(2)
    assert window._content_area.currentIndex() == 2
