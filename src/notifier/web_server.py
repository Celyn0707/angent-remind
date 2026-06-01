from typing import Set
from aiohttp import web, WSMsgType
from .base import BaseNotifier
from src.models import AgentState


class WebNotifier(BaseNotifier):
    """Web 服务通知器"""

    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self._clients: Set[web.WebSocketResponse] = set()
        self._app: web.Application = None
        self._runner: web.AppRunner = None
        self._site: web.TCPSite = None
        self._current_state: dict = {}

    def is_available(self) -> bool:
        """检查通知器是否可用"""
        return self._site is not None

    async def start(self):
        """启动 Web 服务"""
        self._app = web.Application()
        self._app.router.add_get("/ws", self._websocket_handler)
        self._app.router.add_get("/api/status", self._status_handler)
        self._app.router.add_get("/", self._index_handler)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        # 尝试绑定端口，如果占用则尝试下一个
        port = self.port
        while port < self.port + 10:
            try:
                self._site = web.TCPSite(self._runner, self.host, port)
                await self._site.start()
                self.port = port
                print(f"Web 服务已启动: http://{self.host}:{port}")
                break
            except OSError:
                port += 1

        if self._site is None:
            print(f"错误: 无法启动 Web 服务，端口 {self.port}-{self.port + 9} 均被占用")

    async def stop(self):
        """停止 Web 服务"""
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

    async def send(self, state: AgentState) -> bool:
        """发送状态更新"""
        self._current_state = state.to_dict()
        return await self._broadcast(state)

    async def _broadcast(self, state: AgentState) -> bool:
        """广播到所有 WebSocket 客户端"""
        if not self._clients:
            return False

        message = {
            "type": "status_update",
            "data": state.to_dict()
        }

        disconnected = set()
        success_count = 0
        for ws in self._clients:
            try:
                await ws.send_json(message)
                success_count += 1
            except Exception:
                disconnected.add(ws)

        self._clients -= disconnected
        return success_count > 0

    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """WebSocket 连接处理"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._clients.add(ws)

        try:
            # 发送当前状态
            if self._current_state:
                await ws.send_json({
                    "type": "status_update",
                    "data": self._current_state
                })

            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    if msg.data == "close":
                        await ws.close()
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            self._clients.discard(ws)

        return ws

    async def _status_handler(self, request: web.Request) -> web.Response:
        """REST API 状态接口"""
        return web.json_response(self._current_state)

    async def _index_handler(self, request: web.Request) -> web.Response:
        """主页"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Agent 状态监控</title>
        </head>
        <body>
            <h1>Agent 状态监控</h1>
            <p>请在手机上访问此页面</p>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")
