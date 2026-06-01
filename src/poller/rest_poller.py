# src/poller/rest_poller.py
import logging
import requests
from typing import Optional
from .base import BasePoller
from src.models import AgentState

logger = logging.getLogger(__name__)


class RestPoller(BasePoller):
    """REST API 轮询器"""

    def __init__(self, url: str, interval: int = 5, timeout: int = 10,
                 headers: Optional[dict] = None):
        super().__init__(interval)
        self.url = url
        self.timeout = timeout
        self.headers = headers or {}

    def poll(self) -> Optional[AgentState]:
        """执行一次轮询"""
        try:
            response = requests.get(
                self.url,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            state = AgentState.from_dict(data)
            self._notify(state)
            return state
        except Exception as e:
            logger.error("轮询失败: %s", e)
            return None

    def start(self):
        """开始轮询

        注意: 当前为占位实现。实际的轮询循环将在 main.py 中通过 QTimer 实现。
        """
        self._running = True

    def stop(self):
        """停止轮询

        注意: 当前为占位实现。实际的轮询循环将在 main.py 中通过 QTimer 实现。
        """
        self._running = False
