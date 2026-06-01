# src/poller/base.py
from abc import ABC, abstractmethod
from typing import Callable, List, Optional
from src.models import AgentState


class BasePoller(ABC):
    """轮询器基类"""

    def __init__(self, interval: int = 5):
        self.interval = interval
        self._callbacks: List[Callable[[AgentState], None]] = []
        self._running = False

    def on_status_change(self, callback: Callable[[AgentState], None]):
        """注册状态变化回调"""
        self._callbacks.append(callback)

    def _notify(self, state: AgentState):
        """通知所有回调"""
        for callback in self._callbacks:
            callback(state)

    @abstractmethod
    def poll(self) -> Optional[AgentState]:
        """执行一次轮询"""
        pass

    @abstractmethod
    def start(self):
        """开始轮询"""
        pass

    @abstractmethod
    def stop(self):
        """停止轮询"""
        pass
