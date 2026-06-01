# src/state/manager.py
from typing import Callable, List, Optional
from src.models import AgentState


class StateManager:
    """状态管理器"""

    def __init__(self, max_history: int = 1000):
        self._current_state: Optional[AgentState] = None
        self._history: List[AgentState] = []
        self._callbacks: List[Callable[[AgentState], None]] = []
        self._max_history = max_history

    def get_current_state(self) -> Optional[AgentState]:
        """获取当前状态"""
        return self._current_state

    def get_history(self, limit: int = 100) -> List[AgentState]:
        """获取状态历史"""
        return self._history[-limit:]

    def on_state_change(self, callback: Callable[[AgentState], None]):
        """注册状态变化回调"""
        self._callbacks.append(callback)

    def update_state(self, new_state: AgentState):
        """更新状态"""
        if new_state is None or not isinstance(new_state, AgentState):
            return
        # 相同状态不更新
        if self._current_state and self._is_same_state(self._current_state, new_state):
            return

        self._current_state = new_state
        self._history.append(new_state)

        # 限制历史记录数量
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # 通知回调
        self._notify(new_state)

    def _is_same_state(self, state1: AgentState, state2: AgentState) -> bool:
        """判断两个状态是否相同"""
        return (
            state1.status == state2.status
            and state1.task == state2.task
            and state1.progress == state2.progress
            and state1.message == state2.message
        )

    def _notify(self, state: AgentState):
        """通知所有回调"""
        for callback in self._callbacks:
            callback(state)
