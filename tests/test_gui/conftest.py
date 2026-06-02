import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    """创建共享的 QApplication（整个测试会话只创建一次）"""
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    yield instance
    # 不主动销毁 QApplication，避免 teardown 阶段崩溃
