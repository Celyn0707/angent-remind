import requests
from typing import Optional
from .base import BaseNotifier
from src.models import AgentState, StatusType


class WeChatNotifier(BaseNotifier):
    """企业微信通知器"""

    STATUS_TEXT = {
        StatusType.RUNNING: "运行中 ⚡",
        StatusType.COMPLETED: "已完成 ✅",
        StatusType.ERROR: "错误 ❌",
        StatusType.WAITING: "等待中 ⏳",
        StatusType.CONFIRM: "需要确认 ❓"
    }

    def __init__(self, webhook: str, push_on: Optional[list] = None):
        self.webhook = webhook
        self.push_on = push_on or ["running", "completed", "error", "waiting", "confirm"]

    def is_available(self) -> bool:
        """检查通知器是否可用"""
        return bool(self.webhook)

    async def send(self, state: AgentState) -> bool:
        """发送企业微信通知"""
        if not self.is_available():
            return False

        if state.status.value not in self.push_on:
            return False

        message = self._build_message(state)
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }

        try:
            response = requests.post(
                self.webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("errcode") == 0
        except Exception as e:
            print(f"企业微信推送失败: {e}")
            return False

    def _build_message(self, state: AgentState) -> str:
        """构建企业微信消息"""
        status_text = self.STATUS_TEXT.get(state.status, state.status.value)
        progress_bar = self._get_progress_bar(state.progress)

        message = f"## Agent 状态更新\n\n"
        message += f"> **状态：** {status_text}\n"
        message += f"> **任务：** {state.task}\n"
        message += f"> **进度：** {state.progress}% {progress_bar}\n"
        message += f"> **消息：** {state.message}\n"

        if state.error:
            message += f"> **错误：** {state.error}\n"

        return message

    def _get_progress_bar(self, progress: int) -> str:
        """生成进度条"""
        filled = progress // 10
        empty = 10 - filled
        return "█" * filled + "░" * empty
