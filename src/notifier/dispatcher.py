import logging
from typing import List
from .base import BaseNotifier
from src.models import AgentState

logger = logging.getLogger(__name__)


class Dispatcher:
    """事件分发器"""

    def __init__(self):
        self._notifiers: List[BaseNotifier] = []

    def register(self, notifier: BaseNotifier):
        """注册通知器"""
        if notifier not in self._notifiers:
            self._notifiers.append(notifier)

    def unregister(self, notifier: BaseNotifier):
        """注销通知器"""
        if notifier in self._notifiers:
            self._notifiers.remove(notifier)

    async def dispatch(self, state: AgentState):
        """分发状态变化到所有通知器"""
        for notifier in self._notifiers:
            if not notifier.is_available():
                continue
            try:
                await notifier.send(state)
            except Exception as e:
                logger.error("通知器 %s 发送失败: %s", notifier.__class__.__name__, e)
