# src/main.py
import sys
import asyncio
import threading
import signal
import logging
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

logger = logging.getLogger(__name__)


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
        self.bluetooth_notifier = None

        # 初始化轮询器
        self.poller = self._create_poller()

        # 初始化通知器
        self._setup_notifiers()

        # 连接信号
        self._connect_signals()

        # 轮询定时器
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)

        # 异步事件循环（在后台线程中运行）
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_event_loop, daemon=True
        )
        self._loop_thread.start()

    def _run_event_loop(self):
        """在后台线程中运行 asyncio 事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _create_poller(self) -> RestPoller:
        """创建轮询器"""
        return RestPoller(
            url=self.config.api_url,
            interval=self.config.poll_interval,
            timeout=self.config.api_timeout,
            headers=self.config.api_headers
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
            self.bluetooth_notifier = BluetoothNotifier(
                device_name=self.config.bluetooth_device_name,
                auto_reconnect=self.config.bluetooth_auto_reconnect
            )
            self.dispatcher.register(self.bluetooth_notifier)

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
        try:
            self.poller.poll()
        except Exception as e:
            logger.error("轮询执行异常: %s", e)

    async def _start_services(self):
        """启动异步服务"""
        if hasattr(self, 'web_notifier'):
            await self.web_notifier.start()
        if self.bluetooth_notifier is not None:
            await self.bluetooth_notifier.start()

    def run(self):
        """运行程序"""
        # 初始化 UI
        self.renderer.initialize()

        # 启动异步服务
        asyncio.run_coroutine_threadsafe(self._start_services(), self._loop).result()

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

        logger.info("Agent 状态监控已启动")
        logger.info("轮询地址: %s", self.config.api_url)
        logger.info("轮询间隔: %s 秒", self.config.poll_interval)

        # 运行事件循环
        exit_code = self.app.exec()
        self.shutdown()
        return exit_code

    def shutdown(self):
        """关闭程序"""
        self._timer.stop()
        self.renderer.shutdown()

        # 停止异步服务
        stop_coros = []
        if hasattr(self, 'web_notifier'):
            stop_coros.append(self.web_notifier.stop())
        if self.bluetooth_notifier is not None:
            stop_coros.append(self.bluetooth_notifier.stop())

        if stop_coros:
            async def _stop_all():
                for coro in stop_coros:
                    await coro
            asyncio.run_coroutine_threadsafe(_stop_all(), self._loop).result(timeout=5)

        # 停止异步事件循环
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)


def show_gui(config_path: str = None):
    """显示管理控制台"""
    import asyncio
    from src.gui.main_window import MainWindow
    from src.gui.config_panel import ConfigPanel
    from src.gui.status_panel import StatusPanel
    from src.gui.notification_panel import NotificationPanel
    from src.gui.log_panel import LogPanel

    monitor = AgentMonitor(config_path)

    # 创建主窗口
    window = MainWindow()

    # 创建面板
    config_panel = ConfigPanel(monitor.config)
    status_panel = StatusPanel()
    notification_panel = NotificationPanel(monitor.config)
    log_panel = LogPanel()

    # 添加面板到主窗口
    window.add_panel(config_panel, 0)
    window.add_panel(status_panel, 1)
    window.add_panel(notification_panel, 2)
    window.add_panel(log_panel, 3)

    # 连接状态更新信号
    monitor.state_manager.on_state_change(status_panel.update_status)
    monitor.state_manager.on_state_change(
        lambda s: status_panel.update_history(monitor.state_manager.get_history())
    )

    # 启动异步服务（跳过悬浮窗初始化，GUI 模式仅使用管理控制台）
    asyncio.run_coroutine_threadsafe(monitor._start_services(), monitor._loop).result()

    # 启动轮询
    monitor._timer.start(monitor.config.poll_interval * 1000)

    # 显示窗口
    window.show()

    exit_code = monitor.app.exec()
    monitor.shutdown()
    return exit_code


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent 状态提示软件")
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("--gui", action="store_true", help="显示管理控制台")
    args = parser.parse_args()

    if args.gui:
        sys.exit(show_gui(config_path=args.config))
    else:
        monitor = AgentMonitor(args.config)
        sys.exit(monitor.run())


if __name__ == "__main__":
    main()
