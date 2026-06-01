from abc import ABC, abstractmethod
from src.models import AgentState


class BaseNotifier(ABC):
    """通知器基类"""

    @abstractmethod
    async def send(self, state: AgentState) -> bool:
        """发送通知，返回是否成功"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查通知器是否可用"""
        pass
