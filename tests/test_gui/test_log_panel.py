import pytest
from src.gui.log_panel import LogPanel


@pytest.fixture
def panel(app):
    """创建日志面板"""
    return LogPanel()


def test_panel_creation(panel):
    """测试面板创建"""
    assert panel is not None


def test_panel_add_log(panel):
    """测试添加日志"""
    panel.add_log({
        "timestamp": "2026-06-02 10:30:15",
        "type": "运行日志",
        "level": "INFO",
        "message": "轮询成功"
    })

    assert panel._log_table.rowCount() == 1


def test_panel_filter_logs(panel):
    """测试筛选日志"""
    panel.add_log({"timestamp": "10:00:00", "type": "运行日志", "level": "INFO", "message": "test1"})
    panel.add_log({"timestamp": "10:00:01", "type": "错误日志", "level": "ERROR", "message": "test2"})
    panel.add_log({"timestamp": "10:00:02", "type": "运行日志", "level": "INFO", "message": "test3"})

    panel.filter_logs("运行日志", "全部")
    # 只显示运行日志
    visible_count = sum(1 for i in range(panel._log_table.rowCount())
                       if not panel._log_table.isRowHidden(i))
    assert visible_count == 2
