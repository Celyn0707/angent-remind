# src/poller/rest_poller.py
import requests
from typing import Optional
from .base import BasePoller
from src.models import AgentState


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
            return AgentState.from_dict(data)
        except Exception as e:
            print(f"轮询失败: {e}")
            return None

    def start(self):
        """开始轮询"""
        self._running = True

    def stop(self):
        """停止轮询"""
        self._running = False
