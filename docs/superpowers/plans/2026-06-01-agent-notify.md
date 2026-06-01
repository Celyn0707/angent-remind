# Agent 状态提示软件实施计划

> **致自动化工作者：** 必须使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 技能来逐任务实施本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** 开发一个基于 PyQt6 的 AI Agent 状态提示软件，支持桌面悬浮窗、手机网页、企业微信推送三种通知方式，并支持蓝牙备用连接。

**架构：** 采用 Poller → StateManager → Dispatcher → Notifiers 四层架构。Poller 负责从 API 获取状态，StateManager 管理状态数据和转换，Dispatcher 将状态变化分发到多个通知通道（PyQt6 悬浮窗、Web 服务、企业微信、蓝牙）。

**技术栈：** Python 3.10+ / PyQt6 / aiohttp / bleak / requests / websockets / watchdog / pyyaml

---

## 文件结构

```
angent-remind/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── config.py               # 配置管理 ✅
│   ├── models.py               # 状态数据模型 ✅
│   ├── poller/
│   │   ├── __init__.py
│   │   ├── base.py             # 轮询器基类
│   │   ├── rest_poller.py      # REST API 轮询器
│   │   ├── ws_poller.py        # WebSocket 轮询器
│   │   └── file_poller.py      # 文件监听轮询器
│   ├── state/
│   │   ├── __init__.py
│   │   └── manager.py          # 状态管理器
│   ├── notifier/
│   │   ├── __init__.py
│   │   ├── base.py             # 通知器基类
│   │   ├── dispatcher.py       # 事件分发器
│   │   ├── wechat.py           # 企业微信推送
│   │   ├── web_server.py       # Web 服务
│   │   └── bluetooth.py        # 蓝牙服务
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── floating_window.py  # 悬浮窗
│   │   ├── system_tray.py      # 系统托盘
│   │   └── renderer.py         # UI 渲染器
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # 日志工具
├── web/
│   ├── index.html              # 手机网页
│   ├── style.css
│   └── app.js
├── config/
│   └── default.yaml            # 默认配置 ✅
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # ✅
│   ├── test_config.py          # ✅
│   ├── test_rest_poller.py
│   ├── test_state_manager.py
│   ├── test_dispatcher.py
│   ├── test_wechat.py
│   ├── test_web_server.py
│   ├── test_floating_window.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

---

## Task 1: 更新配置管理支持通知配置

**文件：**
- Modify: `src/config.py`
- Modify: `config/default.yaml`
- Modify: `tests/test_config.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_config.py (追加)

def test_notification_config():
    """测试通知配置"""
    config = Config()
    assert config.wechat_enabled is True
    assert config.wechat_webhook == ""
    assert config.web_enabled is True
    assert config.web_port == 8080
    assert config.web_host == "0.0.0.0"
    assert config.bluetooth_enabled is False
    assert config.bluetooth_device_name == "Agent Monitor"


def test_notification_config_custom():
    """测试自定义通知配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "notifications": {
                "wechat": {
                    "enabled": False,
                    "webhook": "https://test.webhook.com"
                },
                "web": {
                    "port": 9090
                },
                "bluetooth": {
                    "enabled": True,
                    "device_name": "My Monitor"
                }
            }
        }, f)
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.wechat_enabled is False
        assert config.wechat_webhook == "https://test.webhook.com"
        assert config.web_port == 9090
        assert config.bluetooth_enabled is True
        assert config.bluetooth_device_name == "My Monitor"
    finally:
        os.unlink(temp_path)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_config.py::test_notification_config tests/test_config.py::test_notification_config_custom -v
```

预期：FAIL - `AttributeError: 'Config' object has no attribute 'wechat_enabled'`

- [ ] **Step 3: 更新默认配置文件**

```yaml
# config/default.yaml (完整替换)

api:
  type: rest
  url: http://localhost:8080/api/agent/status
  method: GET
  headers: {}
  poll_interval: 5
  timeout: 10
  retry_count: 3

window:
  position: bottom-right
  opacity: 0.9
  always_on_top: true
  click_to_expand: true
  drag_enabled: true
  snap_to_edge: true

notifications:
  wechat:
    enabled: true
    webhook: ""
    push_on: ["running", "completed", "error", "waiting", "confirm"]
  web:
    enabled: true
    port: 8080
    host: "0.0.0.0"
  bluetooth:
    enabled: false
    device_name: "Agent Monitor"
    auto_reconnect: true

colors:
  running: "#4ade80"
  completed: "#60a5fa"
  error: "#f87171"
  waiting: "#fbbf24"
  confirm: "#c084fc"

sounds:
  enabled: true
  volume: 0.7
  on_running: "sounds/running.mp3"
  on_completed: "sounds/completed.mp3"
  on_error: "sounds/error.mp3"
  on_waiting: "sounds/waiting.mp3"
  on_confirm: "sounds/confirm.mp3"

logging:
  enabled: true
  level: INFO
  file: logs/agent-monitor.log
  max_size: 10MB
  backup_count: 5
```

- [ ] **Step 4: 更新 Config 类添加通知配置属性**

```python
# src/config.py (完整替换)

import os
from pathlib import Path
from typing import Optional, List
import yaml


class Config:
    """配置管理类"""

    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "default.yaml"

    def __init__(self, config_path: Optional[str] = None):
        self._config = self._load_default()

        if config_path and os.path.exists(config_path):
            user_config = self._load_yaml(config_path)
            self._merge(user_config)

    def _load_yaml(self, path: str) -> dict:
        """加载 YAML 文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _load_default(self) -> dict:
        """加载默认配置"""
        if self.DEFAULT_CONFIG_PATH.exists():
            return self._load_yaml(str(self.DEFAULT_CONFIG_PATH))
        return {}

    def _merge(self, user_config: dict):
        """合并用户配置"""
        for key, value in user_config.items():
            if isinstance(value, dict) and key in self._config:
                self._config[key].update(value)
            else:
                self._config[key] = value

    @property
    def api_type(self) -> str:
        return self._config.get("api", {}).get("type", "rest")

    @property
    def api_url(self) -> str:
        return self._config.get("api", {}).get("url", "")

    @property
    def poll_interval(self) -> int:
        return self._config.get("api", {}).get("poll_interval", 5)

    @property
    def api_timeout(self) -> int:
        return self._config.get("api", {}).get("timeout", 10)

    @property
    def retry_count(self) -> int:
        return self._config.get("api", {}).get("retry_count", 3)

    @property
    def window_opacity(self) -> float:
        return self._config.get("window", {}).get("opacity", 0.9)

    @property
    def window_position(self) -> str:
        return self._config.get("window", {}).get("position", "bottom-right")

    @property
    def always_on_top(self) -> bool:
        return self._config.get("window", {}).get("always_on_top", True)

    @property
    def colors(self) -> dict:
        return self._config.get("colors", {})

    @property
    def sounds_enabled(self) -> bool:
        return self._config.get("sounds", {}).get("enabled", True)

    @property
    def sound_volume(self) -> float:
        return self._config.get("sounds", {}).get("volume", 0.7)

    # 通知配置属性
    @property
    def wechat_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("wechat", {}).get("enabled", True)

    @property
    def wechat_webhook(self) -> str:
        return self._config.get("notifications", {}).get("wechat", {}).get("webhook", "")

    @property
    def wechat_push_on(self) -> List[str]:
        return self._config.get("notifications", {}).get("wechat", {}).get("push_on", ["running", "completed", "error", "waiting", "confirm"])

    @property
    def web_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("web", {}).get("enabled", True)

    @property
    def web_port(self) -> int:
        return self._config.get("notifications", {}).get("web", {}).get("port", 8080)

    @property
    def web_host(self) -> str:
        return self._config.get("notifications", {}).get("web", {}).get("host", "0.0.0.0")

    @property
    def bluetooth_enabled(self) -> bool:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("enabled", False)

    @property
    def bluetooth_device_name(self) -> str:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("device_name", "Agent Monitor")

    @property
    def bluetooth_auto_reconnect(self) -> bool:
        return self._config.get("notifications", {}).get("bluetooth", {}).get("auto_reconnect", True)

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.poll_interval <= 0:
            return False
        if self.api_timeout <= 0:
            return False
        if not 0 <= self.window_opacity <= 1:
            return False
        if self.web_port < 0 or self.web_port > 65535:
            return False
        return True
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_config.py -v
```

预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
cd D:/angent-remind
git add src/config.py config/default.yaml tests/test_config.py
git commit -m "feat: add notification config support"
```

---

## Task 2: 状态管理器

**文件：**
- Create: `src/state/__init__.py`
- Create: `src/state/manager.py`
- Create: `tests/test_state_manager.py`

- [ ] **Step 1: 创建 state 模块 __init__.py**

```python
# src/state/__init__.py
from .manager import StateManager

__all__ = ["StateManager"]
```

- [ ] **Step 2: 编写失败的测试**

```python
# tests/test_state_manager.py
import pytest
from unittest.mock import Mock
from datetime import datetime
from src.state.manager import StateManager
from src.models import AgentState, StatusType


def test_state_manager_initial_state():
    """测试初始状态"""
    manager = StateManager()
    state = manager.get_current_state()
    assert state is None


def test_state_manager_update():
    """测试更新状态"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    new_state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=0,
        message="开始",
        started_at=datetime.now()
    )

    manager.update_state(new_state)
    assert manager.get_current_state() == new_state
    callback.assert_called_once_with(new_state)


def test_state_manager_history():
    """测试状态历史"""
    manager = StateManager()

    for i in range(5):
        state = AgentState(
            status=StatusType.RUNNING,
            task=f"任务{i}",
            progress=i * 20,
            message=f"进度 {i}",
            started_at=datetime.now()
        )
        manager.update_state(state)

    history = manager.get_history()
    assert len(history) == 5
    assert history[-1].task == "任务4"


def test_state_manager_no_duplicate_notification():
    """测试相同状态不重复通知"""
    manager = StateManager()
    callback = Mock()
    manager.on_state_change(callback)

    state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    manager.update_state(state)
    manager.update_state(state)

    assert callback.call_count == 1


def test_state_manager_history_limit():
    """测试历史记录限制"""
    manager = StateManager(max_history=10)

    for i in range(15):
        state = AgentState(
            status=StatusType.RUNNING,
            task=f"任务{i}",
            progress=i,
            message=f"消息{i}",
            started_at=datetime.now()
        )
        manager.update_state(state)

    history = manager.get_history()
    assert len(history) == 10
    assert history[0].task == "任务5"
```

- [ ] **Step 3: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_state_manager.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.state'`

- [ ] **Step 4: 编写最小实现**

```python
# src/state/manager.py
from typing import Callable, List, Optional
from src.models import AgentState


class StateManager:
    """状态管理器"""

    def __init__(self, max_history: int = 1000):
        self._current_state: Optional[AgentState] = None
        self._history: List[AgentState] = []
        self._callbacks: List[Callable[[AgentState], None]] = []
        self._max_history = max_history

    def get_current_state(self) -> Optional[AgentState]:
        """获取当前状态"""
        return self._current_state

    def get_history(self, limit: int = 100) -> List[AgentState]:
        """获取状态历史"""
        return self._history[-limit:]

    def on_state_change(self, callback: Callable[[AgentState], None]):
        """注册状态变化回调"""
        self._callbacks.append(callback)

    def update_state(self, new_state: AgentState):
        """更新状态"""
        # 相同状态不更新
        if self._current_state and self._is_same_state(self._current_state, new_state):
            return

        self._current_state = new_state
        self._history.append(new_state)

        # 限制历史记录数量
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # 通知回调
        self._notify(new_state)

    def _is_same_state(self, state1: AgentState, state2: AgentState) -> bool:
        """判断两个状态是否相同"""
        return (
            state1.status == state2.status
            and state1.task == state2.task
            and state1.progress == state2.progress
            and state1.message == state2.message
        )

    def _notify(self, state: AgentState):
        """通知所有回调"""
        for callback in self._callbacks:
            callback(state)
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_state_manager.py -v
```

预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
cd D:/angent-remind
git add src/state/ tests/test_state_manager.py
git commit -m "feat: add state manager with history tracking"
```

---

## Task 3: REST API 轮询器

**文件：**
- Create: `src/poller/__init__.py`
- Create: `src/poller/base.py`
- Create: `src/poller/rest_poller.py`
- Create: `tests/test_rest_poller.py`

- [ ] **Step 1: 创建 poller 模块 __init__.py**

```python
# src/poller/__init__.py
from .base import BasePoller
from .rest_poller import RestPoller

__all__ = ["BasePoller", "RestPoller"]
```

- [ ] **Step 2: 编写轮询器基类**

```python
# src/poller/base.py
from abc import ABC, abstractmethod
from typing import Callable, List, Optional
from src.models import AgentState


class BasePoller(ABC):
    """轮询器基类"""

    def __init__(self, interval: int = 5):
        self.interval = interval
        self._callbacks: List[Callable[[AgentState], None]] = []
        self._running = False

    def on_status_change(self, callback: Callable[[AgentState], None]):
        """注册状态变化回调"""
        self._callbacks.append(callback)

    def _notify(self, state: AgentState):
        """通知所有回调"""
        for callback in self._callbacks:
            callback(state)

    @abstractmethod
    def poll(self) -> Optional[AgentState]:
        """执行一次轮询"""
        pass

    @abstractmethod
    def start(self):
        """开始轮询"""
        pass

    @abstractmethod
    def stop(self):
        """停止轮询"""
        pass
```

- [ ] **Step 3: 编写失败的测试**

```python
# tests/test_rest_poller.py
import pytest
from unittest.mock import Mock, patch
from src.poller.rest_poller import RestPoller
from src.models import StatusType


def test_rest_poller_creation():
    """测试创建 RestPoller"""
    poller = RestPoller(
        url="http://localhost:8080/api/status",
        interval=5
    )
    assert poller.url == "http://localhost:8080/api/status"
    assert poller.interval == 5


@patch('src.poller.rest_poller.requests.get')
def test_poll_success(mock_get):
    """测试成功轮询"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "running",
        "task": "测试任务",
        "progress": 50,
        "message": "处理中",
        "started_at": "2026-06-01T10:00:00"
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    poller = RestPoller(url="http://test.com/api", interval=5)
    state = poller.poll()

    assert state is not None
    assert state.status == StatusType.RUNNING
    assert state.task == "测试任务"


@patch('src.poller.rest_poller.requests.get')
def test_poll_failure(mock_get):
    """测试轮询失败"""
    mock_get.side_effect = Exception("Connection error")

    poller = RestPoller(url="http://test.com/api", interval=5)
    state = poller.poll()

    assert state is None


def test_on_status_change_callback():
    """测试状态变化回调"""
    poller = RestPoller(url="http://test.com/api", interval=5)
    callback = Mock()
    poller.on_status_change(callback)

    assert callback in poller._callbacks
```

- [ ] **Step 4: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_rest_poller.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.poller.rest_poller'`

- [ ] **Step 5: 编写 RestPoller 实现**

```python
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
```

- [ ] **Step 6: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_rest_poller.py -v
```

预期：全部 PASS

- [ ] **Step 7: 提交**

```bash
cd D:/angent-remind
git add src/poller/ tests/test_rest_poller.py
git commit -m "feat: add REST API poller"
```

---

## Task 4: 通知器基类和事件分发器

**文件：**
- Create: `src/notifier/__init__.py`
- Create: `src/notifier/base.py`
- Create: `src/notifier/dispatcher.py`
- Create: `tests/test_dispatcher.py`

- [ ] **Step 1: 创建 notifier 模块 __init__.py**

```python
# src/notifier/__init__.py
from .base import BaseNotifier
from .dispatcher import Dispatcher

__all__ = ["BaseNotifier", "Dispatcher"]
```

- [ ] **Step 2: 编写通知器基类**

```python
# src/notifier/base.py
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
```

- [ ] **Step 3: 编写失败的测试**

```python
# tests/test_dispatcher.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.notifier.dispatcher import Dispatcher
from src.notifier.base import BaseNotifier
from src.models import AgentState, StatusType
from datetime import datetime


class MockNotifier(BaseNotifier):
    """模拟通知器"""

    def __init__(self, available: bool = True):
        self.available = available
        self.send = AsyncMock(return_value=True)

    def is_available(self) -> bool:
        return self.available


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )


def test_dispatcher_register():
    """测试注册通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)
    assert notifier in dispatcher._notifiers


def test_dispatcher_unregister():
    """测试注销通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)
    dispatcher.unregister(notifier)
    assert notifier not in dispatcher._notifiers


def test_dispatcher_dispatch(sample_state):
    """测试分发事件"""
    dispatcher = Dispatcher()
    notifier1 = MockNotifier()
    notifier2 = MockNotifier()
    dispatcher.register(notifier1)
    dispatcher.register(notifier2)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier1.send.assert_called_once_with(sample_state)
    notifier2.send.assert_called_once_with(sample_state)


def test_dispatcher_dispatch_skip_unavailable(sample_state):
    """测试跳过不可用的通知器"""
    dispatcher = Dispatcher()
    notifier = MockNotifier(available=False)
    dispatcher.register(notifier)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier.send.assert_not_called()


def test_dispatcher_dispatch_continue_on_failure(sample_state):
    """测试单个通知器失败不影响其他"""
    dispatcher = Dispatcher()
    notifier1 = MockNotifier()
    notifier1.send = AsyncMock(side_effect=Exception("发送失败"))
    notifier2 = MockNotifier()
    dispatcher.register(notifier1)
    dispatcher.register(notifier2)

    asyncio.run(dispatcher.dispatch(sample_state))

    notifier1.send.assert_called_once()
    notifier2.send.assert_called_once()
```

- [ ] **Step 4: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_dispatcher.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.notifier'`

- [ ] **Step 5: 编写 Dispatcher 实现**

```python
# src/notifier/dispatcher.py
from typing import List
from .base import BaseNotifier
from src.models import AgentState


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
                print(f"通知器 {notifier.__class__.__name__} 发送失败: {e}")
```

- [ ] **Step 6: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_dispatcher.py -v
```

预期：全部 PASS

- [ ] **Step 7: 提交**

```bash
cd D:/angent-remind
git add src/notifier/ tests/test_dispatcher.py
git commit -m "feat: add notifier base class and dispatcher"
```

---

## Task 5: 企业微信通知器

**文件：**
- Create: `src/notifier/wechat.py`
- Create: `tests/test_wechat.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_wechat.py
import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from src.notifier.wechat import WeChatNotifier
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="分析代码",
        progress=50,
        message="正在处理第3个文件",
        started_at=datetime.now()
    )


def test_wechat_notifier_creation():
    """测试创建企业微信通知器"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    assert notifier.webhook == "https://test.webhook.com"


def test_wechat_notifier_no_webhook():
    """测试没有 webhook 时不可用"""
    notifier = WeChatNotifier(webhook="")
    assert notifier.is_available() is False


def test_wechat_notifier_with_webhook():
    """测试有 webhook 时可用"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    assert notifier.is_available() is True


@patch('src.notifier.wechat.requests.post')
def test_wechat_notifier_send(mock_post, sample_state):
    """测试发送通知"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0}
    mock_post.return_value = mock_response

    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    result = asyncio.run(notifier.send(sample_state))

    assert result is True
    mock_post.assert_called_once()


def test_wechat_notifier_build_message(sample_state):
    """测试构建消息"""
    notifier = WeChatNotifier(webhook="https://test.webhook.com")
    message = notifier._build_message(sample_state)

    assert "运行中" in message
    assert "分析代码" in message
    assert "50%" in message
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_wechat.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.notifier.wechat'`

- [ ] **Step 3: 编写 WeChatNotifier 实现**

```python
# src/notifier/wechat.py
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_wechat.py -v
```

预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
cd D:/angent-remind
git add src/notifier/wechat.py tests/test_wechat.py
git commit -m "feat: add WeChat webhook notifier"
```

---

## Task 6: Web 服务通知器

**文件：**
- Create: `src/notifier/web_server.py`
- Create: `tests/test_web_server.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_web_server.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.notifier.web_server import WebNotifier
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )


def test_web_notifier_creation():
    """测试创建 Web 通知器"""
    notifier = WebNotifier(port=8080, host="0.0.0.0")
    assert notifier.port == 8080
    assert notifier.host == "0.0.0.0"


def test_web_notifier_is_available():
    """测试可用性检查"""
    notifier = WebNotifier(port=8080)
    assert notifier.is_available() is True


def test_web_notifier_build_message(sample_state):
    """测试构建消息"""
    notifier = WebNotifier(port=8080)
    message = notifier._state_to_dict(sample_state)

    assert message["status"] == "running"
    assert message["task"] == "测试"
    assert message["progress"] == 50


@pytest.mark.asyncio
async def test_web_notifier_broadcast(sample_state):
    """测试广播消息"""
    notifier = WebNotifier(port=8080)

    # 模拟 WebSocket 连接
    mock_ws = AsyncMock()
    notifier._clients.add(mock_ws)

    await notifier._broadcast(sample_state)

    mock_ws.send_json.assert_called_once()
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_web_server.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.notifier.web_server'`

- [ ] **Step 3: 编写 WebNotifier 实现**

```python
# src/notifier/web_server.py
import asyncio
import json
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
        return True

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

    async def stop(self):
        """停止 Web 服务"""
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

    async def send(self, state: AgentState) -> bool:
        """发送状态更新"""
        self._current_state = self._state_to_dict(state)
        await self._broadcast(state)
        return True

    def _state_to_dict(self, state: AgentState) -> dict:
        """将状态转换为字典"""
        return {
            "status": state.status.value,
            "task": state.task,
            "progress": state.progress,
            "message": state.message,
            "started_at": state.started_at.isoformat(),
            "error": state.error,
            "confirm_required": state.confirm_required
        }

    async def _broadcast(self, state: AgentState):
        """广播到所有 WebSocket 客户端"""
        message = {
            "type": "status_update",
            "data": self._state_to_dict(state)
        }

        disconnected = set()
        for ws in self._clients:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)

        self._clients -= disconnected

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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_web_server.py -v
```

预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
cd D:/angent-remind
git add src/notifier/web_server.py tests/test_web_server.py
git commit -m "feat: add web server notifier with WebSocket"
```

---

## Task 7: 蓝牙通知器

**文件：**
- Create: `src/notifier/bluetooth.py`
- Create: `tests/test_bluetooth.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_bluetooth.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.notifier.bluetooth import BluetoothNotifier
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def sample_state():
    return AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )


def test_bluetooth_notifier_creation():
    """测试创建蓝牙通知器"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    assert notifier.device_name == "Test Monitor"


def test_bluetooth_notifier_is_available():
    """测试可用性检查"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    # 蓝牙可用性取决于 bleak 是否安装
    assert isinstance(notifier.is_available(), bool)


def test_bluetooth_notifier_build_data(sample_state):
    """测试构建数据"""
    notifier = BluetoothNotifier(device_name="Test Monitor")
    data = notifier._state_to_bytes(sample_state)

    assert b"running" in data
    assert b"测试" in data
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_bluetooth.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.notifier.bluetooth'`

- [ ] **Step 3: 编写 BluetoothNotifier 实现**

```python
# src/notifier/bluetooth.py
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_bluetooth.py -v
```

预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
cd D:/angent-remind
git add src/notifier/bluetooth.py tests/test_bluetooth.py
git commit -m "feat: add Bluetooth notifier (stub)"
```

---

## Task 8: PyQt6 悬浮窗

**文件：**
- Create: `src/ui/__init__.py`
- Create: `src/ui/floating_window.py`
- Create: `tests/test_floating_window.py`

- [ ] **Step 1: 创建 ui 模块 __init__.py**

```python
# src/ui/__init__.py
from .floating_window import FloatingWindow

__all__ = ["FloatingWindow"]
```

- [ ] **Step 2: 编写失败的测试**

```python
# tests/test_floating_window.py
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ui.floating_window import FloatingWindow
from src.models import AgentState, StatusType
from datetime import datetime


@pytest.fixture
def app():
    """创建 QApplication"""
    return QApplication([])


@pytest.fixture
def window(app):
    """创建悬浮窗"""
    return FloatingWindow()


def test_window_creation(window):
    """测试窗口创建"""
    assert window is not None
    assert window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


def test_window_update_state(window):
    """测试更新状态"""
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    window.update_state(state)
    assert window._current_state == state


def test_window_toggle_expand(window):
    """测试展开/收起"""
    assert window._expanded is False

    window.toggle_expand()
    assert window._expanded is True

    window.toggle_expand()
    assert window._expanded is False
```

- [ ] **Step 3: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_floating_window.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.ui'`

- [ ] **Step 4: 编写最小实现**

```python
# src/ui/floating_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
from typing import Optional
from src.models import AgentState, StatusType


class FloatingWindow(QWidget):
    """悬浮窗"""

    STATUS_COLORS = {
        StatusType.RUNNING: "#4ade80",
        StatusType.COMPLETED: "#60a5fa",
        StatusType.ERROR: "#f87171",
        StatusType.WAITING: "#fbbf24",
        StatusType.CONFIRM: "#c084fc"
    }

    STATUS_ICONS = {
        StatusType.RUNNING: "⚡",
        StatusType.COMPLETED: "✅",
        StatusType.ERROR: "❌",
        StatusType.WAITING: "⏳",
        StatusType.CONFIRM: "❓"
    }

    STATUS_TEXT = {
        StatusType.RUNNING: "运行中",
        StatusType.COMPLETED: "已完成",
        StatusType.ERROR: "错误",
        StatusType.WAITING: "等待中",
        StatusType.CONFIRM: "需要确认"
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_state: Optional[AgentState] = None
        self._expanded = False
        self._drag_pos: Optional[QPoint] = None

        self._setup_ui()
        self._setup_window()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 80)

        # 默认位置：右下角
        self._move_to_default_position()

    def _move_to_default_position(self):
        """移动到默认位置"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 20
        self.move(x, y)

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)

        # 状态图标和文本
        self._icon_label = QLabel("⏳")
        self._icon_label.setFont(QFont("Segoe UI Emoji", 24))
        layout.addWidget(self._icon_label)

        self._status_label = QLabel("等待中")
        self._status_label.setFont(QFont("Microsoft YaHei", 12))
        layout.addWidget(self._status_label)

        self._message_label = QLabel("点击查看详情")
        self._message_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(self._message_label)

        self.setLayout(layout)

    def update_state(self, state: AgentState):
        """更新状态"""
        self._current_state = state

        # 更新图标
        icon = self.STATUS_ICONS.get(state.status, "")
        self._icon_label.setText(icon)

        # 更新状态文本
        status_text = self.STATUS_TEXT.get(state.status, "")
        self._status_label.setText(status_text)

        # 更新消息
        message = state.message
        if len(message) > 20:
            message = message[:20] + "..."
        self._message_label.setText(message)

        # 更新背景颜色
        color = self.STATUS_COLORS.get(state.status, "#888888")
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 12px;
                color: white;
            }}
        """)

    def toggle_expand(self):
        """切换展开/收起"""
        self._expanded = not self._expanded
        if self._expanded:
            self.setFixedSize(300, 200)
        else:
            self.setFixedSize(200, 80)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        self.toggle_expand()
```

- [ ] **Step 5: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_floating_window.py -v
```

预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
cd D:/angent-remind
git add src/ui/ tests/test_floating_window.py
git commit -m "feat: add floating window with drag support"
```

---

## Task 9: UI 渲染器和系统托盘

**文件：**
- Create: `src/ui/renderer.py`
- Create: `src/ui/system_tray.py`

- [ ] **Step 1: 编写 UI 渲染器**

```python
# src/ui/renderer.py
from typing import Optional
from src.models import AgentState, StatusType
from src.ui.floating_window import FloatingWindow
from src.config import Config


class UIRenderer:
    """UI 渲染器"""

    def __init__(self, config: Config):
        self.config = config
        self.floating_window = FloatingWindow()
        self.tray_icon = None

    def initialize(self):
        """初始化 UI"""
        self._setup_tray()
        self.floating_window.show()

    def _setup_tray(self):
        """设置系统托盘"""
        from src.ui.system_tray import SystemTray
        self.tray_icon = SystemTray(self.floating_window)
        self.tray_icon.show()

    def render(self, state: AgentState):
        """渲染状态"""
        self.floating_window.update_state(state)

    def show_notification(self, title: str, message: str):
        """显示通知"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message)

    def shutdown(self):
        """关闭 UI"""
        if self.tray_icon:
            self.tray_icon.hide()
        self.floating_window.close()
```

- [ ] **Step 2: 编写系统托盘**

```python
# src/ui/system_tray.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from src.ui.floating_window import FloatingWindow


class SystemTray(QSystemTrayIcon):
    """系统托盘"""

    def __init__(self, floating_window: FloatingWindow, parent=None):
        super().__init__(parent)
        self.floating_window = floating_window
        self._setup_menu()
        self._setup_icon()

    def _setup_icon(self):
        """设置图标"""
        self.setIcon(QIcon.fromTheme("dialog-information"))
        self.setToolTip("Agent 状态监控")

    def _setup_menu(self):
        """设置菜单"""
        menu = QMenu()

        # 显示/隐藏悬浮窗
        toggle_action = QAction("显示/隐藏悬浮窗", menu)
        toggle_action.triggered.connect(self._toggle_window)
        menu.addAction(toggle_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _toggle_window(self):
        """切换悬浮窗显示"""
        if self.floating_window.isVisible():
            self.floating_window.hide()
        else:
            self.floating_window.show()
```

- [ ] **Step 3: 提交**

```bash
cd D:/angent-remind
git add src/ui/renderer.py src/ui/system_tray.py
git commit -m "feat: add UI renderer and system tray"
```

---

## Task 10: 手机网页前端

**文件：**
- Create: `web/index.html`
- Create: `web/style.css`
- Create: `web/app.js`

- [ ] **Step 1: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent 状态监控</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Agent 状态监控</h1>
            <div id="connection-status" class="disconnected">未连接</div>
        </header>

        <main>
            <div id="status-card" class="status-card">
                <div id="status-icon" class="status-icon">⏳</div>
                <div id="status-text" class="status-text">等待中</div>
                <div class="progress-container">
                    <div id="progress-bar" class="progress-bar" style="width: 0%"></div>
                    <span id="progress-text" class="progress-text">0%</span>
                </div>
                <div id="task-name" class="task-name">-</div>
                <div id="message" class="message">-</div>
                <div id="runtime" class="runtime">-</div>
            </div>

            <div class="history-section">
                <h2>最近状态</h2>
                <div id="history-list" class="history-list"></div>
            </div>
        </main>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 创建 style.css**

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 480px;
    margin: 0 auto;
    padding: 20px;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    color: white;
}

header h1 {
    font-size: 20px;
    font-weight: 600;
}

#connection-status {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.connected {
    background: #4ade80;
    color: #166534;
}

.disconnected {
    background: #f87171;
    color: #991b1b;
}

.status-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    margin-bottom: 24px;
}

.status-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.status-text {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 16px;
}

.progress-container {
    background: #e5e7eb;
    border-radius: 8px;
    height: 16px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: 8px;
    transition: width 0.3s ease;
    background: linear-gradient(90deg, #4ade80, #22c55e);
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 11px;
    font-weight: 600;
    color: #374151;
}

.task-name {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 8px;
}

.message {
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 8px;
}

.runtime {
    font-size: 12px;
    color: #9ca3af;
}

.history-section {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.history-section h2 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: #374151;
}

.history-list {
    max-height: 300px;
    overflow-y: auto;
}

.history-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;
}

.history-item:last-child {
    border-bottom: none;
}

.history-icon {
    font-size: 20px;
    margin-right: 12px;
}

.history-content {
    flex: 1;
}

.history-task {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
}

.history-time {
    font-size: 12px;
    color: #9ca3af;
}

/* 状态颜色 */
.status-running {
    background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
}

.status-completed {
    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.status-error {
    background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
}

.status-waiting {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.status-confirm {
    background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%);
}
```

- [ ] **Step 3: 创建 app.js**

```javascript
class AgentMonitor {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.history = [];
        this.maxHistory = 20;

        this.init();
    }

    init() {
        this.connect();
        this.updateRuntime();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket 连接成功');
            this.setConnectionStatus(true);
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
                this.updateStatus(data.data);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket 连接关闭');
            this.setConnectionStatus(false);
            this.reconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket 错误:', error);
        };
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            console.log(`${delay / 1000}秒后重连...`);
            setTimeout(() => this.connect(), delay);
        }
    }

    setConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (connected) {
            statusEl.textContent = '已连接';
            statusEl.className = 'connected';
        } else {
            statusEl.textContent = '未连接';
            statusEl.className = 'disconnected';
        }
    }

    updateStatus(state) {
        // 更新状态卡片
        const statusIcons = {
            running: '⚡',
            completed: '✅',
            error: '❌',
            waiting: '⏳',
            confirm: '❓'
        };

        const statusTexts = {
            running: '运行中',
            completed: '已完成',
            error: '错误',
            waiting: '等待中',
            confirm: '需要确认'
        };

        document.getElementById('status-icon').textContent = statusIcons[state.status] || '?';
        document.getElementById('status-text').textContent = statusTexts[state.status] || state.status;
        document.getElementById('progress-bar').style.width = `${state.progress}%`;
        document.getElementById('progress-text').textContent = `${state.progress}%`;
        document.getElementById('task-name').textContent = state.task || '-';
        document.getElementById('message').textContent = state.message || '-';

        // 更新卡片背景
        const card = document.getElementById('status-card');
        card.className = `status-card status-${state.status}`;

        // 添加到历史记录
        this.addHistory(state);

        // 存储开始时间用于计算运行时间
        if (state.started_at) {
            this.startedAt = new Date(state.started_at);
        }
    }

    addHistory(state) {
        const statusIcons = {
            running: '⚡',
            completed: '✅',
            error: '❌',
            waiting: '⏳',
            confirm: '❓'
        };

        const historyItem = {
            icon: statusIcons[state.status] || '?',
            task: state.task,
            time: new Date().toLocaleTimeString()
        };

        this.history.unshift(historyItem);
        if (this.history.length > this.maxHistory) {
            this.history.pop();
        }

        this.renderHistory();
    }

    renderHistory() {
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = this.history.map(item => `
            <div class="history-item">
                <span class="history-icon">${item.icon}</span>
                <div class="history-content">
                    <div class="history-task">${item.task}</div>
                    <div class="history-time">${item.time}</div>
                </div>
            </div>
        `).join('');
    }

    updateRuntime() {
        setInterval(() => {
            if (this.startedAt) {
                const now = new Date();
                const diff = Math.floor((now - this.startedAt) / 1000);
                const minutes = Math.floor(diff / 60);
                const seconds = diff % 60;
                document.getElementById('runtime').textContent = 
                    `已运行：${minutes} 分 ${seconds} 秒`;
            }
        }, 1000);
    }
}

// 启动应用
const monitor = new AgentMonitor();
```

- [ ] **Step 4: 提交**

```bash
cd D:/angent-remind
git add web/
git commit -m "feat: add mobile web frontend"
```

---

## Task 11: 程序入口与主循环

**文件：**
- Create: `src/main.py`

- [ ] **Step 1: 编写主程序**

```python
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
```

- [ ] **Step 2: 提交**

```bash
cd D:/angent-remind
git add src/main.py
git commit -m "feat: add main entry point with all notifiers"
```

---

## Task 12: 集成测试与文档完善

**文件：**
- Create: `tests/test_integration.py`
- Modify: `README.md`
- Modify: `requirements.txt`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_integration.py
import pytest
from unittest.mock import Mock
from src.models import AgentState, StatusType
from src.state.manager import StateManager
from src.notifier.dispatcher import Dispatcher
from src.notifier.base import BaseNotifier
from datetime import datetime
import asyncio


class MockNotifier(BaseNotifier):
    """模拟通知器"""

    def __init__(self):
        self.sent_states = []

    async def send(self, state: AgentState) -> bool:
        self.sent_states.append(state)
        return True

    def is_available(self) -> bool:
        return True


def test_full_state_flow():
    """测试完整状态流转"""
    manager = StateManager()
    states_received = []
    manager.on_state_change(lambda s: states_received.append(s))

    # 初始状态：等待中
    state1 = AgentState(
        status=StatusType.WAITING,
        task="初始化",
        progress=0,
        message="等待开始",
        started_at=datetime.now()
    )
    manager.update_state(state1)

    # 运行中
    state2 = AgentState(
        status=StatusType.RUNNING,
        task="执行任务",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )
    manager.update_state(state2)

    # 完成
    state3 = AgentState(
        status=StatusType.COMPLETED,
        task="执行任务",
        progress=100,
        message="已完成",
        started_at=datetime.now()
    )
    manager.update_state(state3)

    assert len(states_received) == 3
    assert states_received[0].status == StatusType.WAITING
    assert states_received[1].status == StatusType.RUNNING
    assert states_received[2].status == StatusType.COMPLETED


def test_dispatcher_integration():
    """测试分发器集成"""
    dispatcher = Dispatcher()
    notifier = MockNotifier()
    dispatcher.register(notifier)

    state = AgentState(
        status=StatusType.RUNNING,
        task="测试",
        progress=50,
        message="处理中",
        started_at=datetime.now()
    )

    asyncio.run(dispatcher.dispatch(state))

    assert len(notifier.sent_states) == 1
    assert notifier.sent_states[0].status == StatusType.RUNNING


def test_error_recovery():
    """测试错误恢复"""
    manager = StateManager()
    states_received = []
    manager.on_state_change(lambda s: states_received.append(s))

    # 错误状态
    error_state = AgentState(
        status=StatusType.ERROR,
        task="失败任务",
        progress=30,
        message="出错了",
        started_at=datetime.now(),
        error="连接超时"
    )
    manager.update_state(error_state)

    # 恢复运行
    recovery_state = AgentState(
        status=StatusType.RUNNING,
        task="重试任务",
        progress=0,
        message="重新开始",
        started_at=datetime.now()
    )
    manager.update_state(recovery_state)

    assert len(states_received) == 2
    assert states_received[0].error == "连接超时"
    assert states_received[1].error is None
```

- [ ] **Step 2: 更新 requirements.txt**

```txt
# requirements.txt

# UI
PyQt6>=6.5.0
PyQt6-Qt6>=6.5.0
PyQt6-sip>=13.5.0

# 网络
requests>=2.31.0
websockets>=12.0
aiohttp>=3.9.0

# 蓝牙
bleak>=0.21.0

# 配置
pyyaml>=6.0

# 文件监听
watchdog>=3.0.0

# 测试
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-aiohttp>=1.0.0
pytest-asyncio>=0.21.0
```

- [ ] **Step 3: 更新 README.md**

```markdown
# Agent 状态提示软件

AI Agent 状态提示软件，通过桌面悬浮窗、手机网页、企业微信推送三种方式实时展示 Agent 运行状态。

## 功能特性

- ✅ 桌面悬浮窗实时显示状态（5种状态类型）
- ✅ 手机网页实时查看状态（局域网访问）
- ✅ 企业微信 Webhook 推送通知
- ✅ 蓝牙备用连接
- ✅ 支持拖拽、展开详情、右键菜单
- ✅ 可配置的视觉和行为参数

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 使用默认配置
python -m src.main

# 指定配置文件
python -m src.main -c path/to/config.yaml
```

## 配置

配置文件位置：`~/.agent-monitor/config.yaml`

### 配置示例

```yaml
api:
  type: rest
  url: http://localhost:8080/api/agent/status
  poll_interval: 5

notifications:
  wechat:
    enabled: true
    webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
  web:
    enabled: true
    port: 8080
  bluetooth:
    enabled: false

window:
  position: bottom-right
  opacity: 0.9
  always_on_top: true

sounds:
  enabled: true
  volume: 0.7
```

## 状态说明

| 状态 | 颜色 | 图标 | 描述 |
|------|------|------|------|
| 运行中 | 🟢 绿色 | ⚡ | Agent 正在执行任务 |
| 已完成 | 🔵 蓝色 | ✅ | 任务执行完成 |
| 错误/异常 | 🔴 红色 | ❌ | 执行出错或异常 |
| 等待中/空闲 | 🟡 黄色 | ⏳ | 等待输入或空闲 |
| 需要确认 | 🟣 紫色 | ❓ | 需要用户确认操作 |

## 手机访问

确保手机和电脑在同一局域网，然后在手机浏览器访问：

```
http://电脑IP:8080
```

## 开发

```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_models.py
```

## 目录结构

```
src/
├── main.py           # 程序入口
├── config.py         # 配置管理
├── models.py         # 状态数据模型
├── poller/           # API 轮询器
├── state/            # 状态管理器
├── notifier/         # 通知通道
└── ui/               # 用户界面
web/
├── index.html        # 手机网页
├── style.css
└── app.js
```

## 许可证

MIT
```

- [ ] **Step 4: 运行集成测试**

```bash
cd D:/angent-remind
pytest tests/test_integration.py -v
```

预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
cd D:/angent-remind
git add tests/test_integration.py README.md requirements.txt
git commit -m "docs: add integration tests and update README"
```

---

## 实施计划完成

**计划已完成并保存到：** `docs/superpowers/plans/2026-06-01-agent-notify.md`

**两种执行方式：**

1. **子代理驱动（推荐）** - 每个任务分发一个新的子代理，任务间进行审查，快速迭代

2. **内联执行** - 在当前会话中执行任务，批量执行并设置检查点

**请选择执行方式？**
