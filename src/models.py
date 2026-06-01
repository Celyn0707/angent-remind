from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class StatusType(Enum):
    """Agent 状态类型"""
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"
    CONFIRM = "confirm"


@dataclass
class AgentState:
    """Agent 状态数据"""
    status: StatusType
    task: str
    progress: int
    message: str
    started_at: datetime
    error: Optional[str] = None
    confirm_required: bool = False

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "status": self.status.value,
            "task": self.task,
            "progress": self.progress,
            "message": self.message,
            "started_at": self.started_at.isoformat(),
            "error": self.error,
            "confirm_required": self.confirm_required
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentState":
        """从字典创建"""
        return cls(
            status=StatusType(data["status"]),
            task=data["task"],
            progress=data["progress"],
            message=data["message"],
            started_at=datetime.fromisoformat(data["started_at"]),
            error=data.get("error"),
            confirm_required=data.get("confirm_required", False)
        )
