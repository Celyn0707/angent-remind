# src/main.py
import sys
import asyncio
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.config import Config
from src.models import AgentState, StatusType
from src.poller.rest_poller import RestPoller
from src.state.manager import StateManager
from src.notifier.dispatcher import Dispatcher
from src.notifier.wechat import WeChatNotifier
from src.notifier.web_server import WebNotifier
from src.notifier.bluetooth import BluetoothNotifier
from src.ui.renderer import UIRenderer
from datetime import datetime


class AgentMonitor:
    """Agent 状态监控主程序"""

    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 初始化组件
        self.state_manager = StateManager()
        self.dispatcher = Dispatcher()
        self.renderer = UIRenderer(self.config)

        # 初始化轮询器
        self.poller = self._create_poller()

        # 初始化通知器
        self._setup_notifiers()

        # 连接信号
        self._connect_signals()

        # 轮询定时器
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)

        # 异步事件循环
        self._loop = asyncio.new_event_loop()

    def _create_poller(self) -> RestPoller:
        """创建轮询器"""
        return RestPoller(
            url=self.config.api_url,
            interval=self.config.poll_interval,
            timeout=self.config.api_timeout,
            headers=self.config._config.get("api", {}).get("headers", {})
        )

    def _setup_notifiers(self):
        """设置通知器"""
        # 企业微信通知器
        if self.config.wechat_enabled:
            wechat = WeChatNotifier(
                webhook=self.config.wechat_webhook,
                push_on=self.config.wechat_push_on
            )
            self.dispatcher.register(wechat)

        # Web 服务通知器
        if self.config.web_enabled:
            self.web_notifier = WebNotifier(
                port=self.config.web_port,
                host=self.config.web_host
            )
            self.dispatcher.register(self.web_notifier)

        # 蓝牙通知器
        if self.config.bluetooth_enabled:
            bluetooth = BluetoothNotifier(
                device_name=self.config.bluetooth_device_name,
                auto_reconnect=self.config.bluetooth_auto_reconnect
            )
            self.dispatcher.register(bluetooth)

    def _connect_signals(self):
        """连接信号"""
        # 状态变化时更新 UI
        self.state_manager.on_state_change(self.renderer.render)

        # 状态变化时分发到通知器
        self.state_manager.on_state_change(self._dispatch_state)

        # 轮询器状态变化时更新状态管理器
        self.poller.on_status_change(self.state_manager.update_state)

    def _dispatch_state(self, state: AgentState):
        """分发状态到通知器"""
        asyncio.run_coroutine_threadsafe(
            self.dispatcher.dispatch(state),
            self._loop
        )

    def _poll(self):
        """执行轮询"""
        state = self.poller.poll()
        if state:
            self.state_manager.update_state(state)

    async def _start_services(self):
        """启动异步服务"""
        if hasattr(self, 'web_notifier'):
            await self.web_notifier.start()

    def run(self):
        """运行程序"""
        # 初始化 UI
        self.renderer.initialize()

        # 启动异步服务
        self._loop.run_until_complete(self._start_services())

        # 启动轮询
        self._timer.start(self.config.poll_interval * 1000)

        # 设置信号处理
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # 显示初始状态
        initial_state = AgentState(
            status=StatusType.WAITING,
            task="等待连接",
            progress=0,
            message="正在连接 Agent...",
            started_at=datetime.now()
        )
        self.renderer.render(initial_state)

        print("Agent 状态监控已启动")
        print(f"轮询地址: {self.config.api_url}")
        print(f"轮询间隔: {self.config.poll_interval} 秒")

        # 运行事件循环
        return self.app.exec()

    def shutdown(self):
        """关闭程序"""
        self._timer.stop()
        self.renderer.shutdown()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent 状态提示软件")
    parser.add_argument("-c", "--config", help="配置文件路径")
    args = parser.parse_args()

    monitor = AgentMonitor(args.config)
    sys.exit(monitor.run())


if __name__ == "__main__":
    main()
