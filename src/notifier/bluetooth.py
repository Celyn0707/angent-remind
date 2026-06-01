import json
import asyncio
from typing import Optional
from .base import BaseNotifier
from src.models import AgentState

try:
    from bleak import BleakGATTServer, BleakGATTCharacteristic
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False


class BluetoothNotifier(BaseNotifier):
    """蓝牙通知器"""

    # GATT Service UUID
    SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

    # Characteristic UUIDs
    STATUS_UUID = "12345678-1234-5678-1234-56789abcdef1"
    TASK_UUID = "12345678-1234-5678-1234-56789abcdef2"
    PROGRESS_UUID = "12345678-1234-5678-1234-56789abcdef3"
    MESSAGE_UUID = "12345678-1234-5678-1234-56789abcdef4"

    def __init__(self, device_name: str = "Agent Monitor", auto_reconnect: bool = True):
        self.device_name = device_name
        self.auto_reconnect = auto_reconnect
        self._server: Optional[BleakGATTServer] = None
        self._connected = False

    def is_available(self) -> bool:
        """检查蓝牙是否可用"""
        return BLEAK_AVAILABLE

    async def start(self):
        """启动蓝牙服务"""
        if not BLEAK_AVAILABLE:
            print("bleak 未安装，蓝牙服务不可用")
            return

        try:
            self._server = BleakGATTServer()
            # TODO: 添加 GATT Service 和 Characteristics
            await self._server.start()
            print(f"蓝牙服务已启动: {self.device_name}")
        except Exception as e:
            print(f"蓝牙服务启动失败: {e}")

    async def stop(self):
        """停止蓝牙服务"""
        if self._server:
            await self._server.stop()

    async def send(self, state: AgentState) -> bool:
        """通过蓝牙发送状态"""
        if not BLEAK_AVAILABLE or not self._server:
            return False

        try:
            data = self._state_to_bytes(state)
            # TODO: 通过 GATT Characteristic Notify 发送数据
            return True
        except Exception as e:
            print(f"蓝牙发送失败: {e}")
            return False

    def _state_to_bytes(self, state: AgentState) -> bytes:
        """将状态转换为字节"""
        data = {
            "status": state.status.value,
            "task": state.task,
            "progress": state.progress,
            "message": state.message
        }
        return json.dumps(data, ensure_ascii=False).encode("utf-8")
