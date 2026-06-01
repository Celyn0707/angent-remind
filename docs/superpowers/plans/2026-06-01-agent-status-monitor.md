# Agent 状态提示软件实施计划

> **致自动化工作者：** 必须使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 技能来逐任务实施本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

**目标：** 开发一个基于 PyQt6 的 AI Agent 状态提示软件，通过悬浮窗实时展示 Agent 运行状态。

**架构：** 采用 Poller → StateManager → Renderer 三层架构。Poller 负责从 API 获取状态，StateManager 管理状态数据和转换，Renderer 负责 UI 渲染和交互。

**技术栈：** Python 3.10+ / PyQt6 / requests / websockets / watchdog / pyyaml

---

## 文件结构

```
angent-remind/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── config.py               # 配置管理
│   ├── models.py               # 状态数据模型
│   ├── poller/
│   │   ├── __init__.py
│   │   ├── base.py             # 轮询器基类
│   │   ├── rest_poller.py      # REST API 轮询器
│   │   ├── ws_poller.py        # WebSocket 轮询器
│   │   └── file_poller.py      # 文件监听轮询器
│   ├── state/
│   │   ├── __init__.py
│   │   └── manager.py          # 状态管理器
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── floating_window.py  # 悬浮窗
│   │   ├── system_tray.py      # 系统托盘
│   │   └── renderer.py         # UI 渲染器
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # 日志工具
├── config/
│   └── default.yaml            # 默认配置
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_config.py
│   ├── test_rest_poller.py
│   ├── test_state_manager.py
│   └── test_floating_window.py
├── requirements.txt
└── README.md
```

---

## Task 1: 项目初始化与依赖配置

**文件：**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `README.md`

- [ ] **Step 1: 创建 requirements.txt**

```txt
PyQt6>=6.5.0
PyQt6-Qt6>=6.5.0
PyQt6-sip>=13.5.0
requests>=2.31.0
websockets>=12.0
pyyaml>=6.0
watchdog>=3.0.0
pytest>=7.4.0
pytest-qt>=4.2.0
```

- [ ] **Step 2: 创建 src/__init__.py**

```python
"""Agent 状态提示软件"""
```

- [ ] **Step 3: 创建 tests/__init__.py**

```python
"""测试模块"""
```

- [ ] **Step 4: 创建 README.md**

```markdown
# Agent 状态提示软件

AI Agent 状态提示软件，通过悬浮窗实时展示 Agent 运行状态。

## 功能特性

- 实时监控 Agent 状态（REST API / WebSocket / 文件监听）
- 悬浮窗展示状态信息
- 5 种状态类型：运行中、已完成、错误/异常、等待中/空闲、需要确认
- 支持拖拽、展开详情、右键菜单、声音提醒

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python -m src.main
```

## 配置

配置文件位置：`~/.agent-monitor/config.yaml`

详见 `config/default.yaml` 示例。
```

- [ ] **Step 5: 安装依赖并验证**

```bash
cd D:/angent-remind
pip install -r requirements.txt
```

- [ ] **Step 6: 初始化 Git 仓库并提交**

```bash
cd D:/angent-remind
git init
git add .
git commit -m "chore: initialize project structure"
```

---

## Task 2: 状态数据模型

**文件：**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_models.py
import pytest
from datetime import datetime
from src.models import AgentState, StatusType


def test_status_type_enum():
    """测试状态类型枚举"""
    assert StatusType.RUNNING.value == "running"
    assert StatusType.COMPLETED.value == "completed"
    assert StatusType.ERROR.value == "error"
    assert StatusType.WAITING.value == "waiting"
    assert StatusType.CONFIRM.value == "confirm"


def test_agent_state_creation():
    """测试创建 AgentState"""
    state = AgentState(
        status=StatusType.RUNNING,
        task="分析代码",
        progress=50,
        message="正在处理...",
        started_at=datetime.now()
    )
    assert state.status == StatusType.RUNNING
    assert state.task == "分析代码"
    assert state.progress == 50
    assert state.error is None
    assert state.confirm_required is False


def test_agent_state_to_dict():
    """测试 AgentState 转换为字典"""
    now = datetime.now()
    state = AgentState(
        status=StatusType.RUNNING,
        task="测试任务",
        progress=75,
        message="处理中",
        started_at=now
    )
    d = state.to_dict()
    assert d["status"] == "running"
    assert d["task"] == "测试任务"
    assert d["progress"] == 75
    assert d["started_at"] == now.isoformat()


def test_agent_state_from_dict():
    """测试从字典创建 AgentState"""
    now = datetime.now()
    data = {
        "status": "error",
        "task": "测试任务",
        "progress": 30,
        "message": "出错了",
        "started_at": now.isoformat(),
        "error": "连接超时",
        "confirm_required": False
    }
    state = AgentState.from_dict(data)
    assert state.status == StatusType.ERROR
    assert state.error == "连接超时"


def test_invalid_status():
    """测试无效状态类型"""
    with pytest.raises(ValueError):
        StatusType("invalid_status")
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_models.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.models'`

- [ ] **Step 3: 编写最小实现**

```python
# src/models.py
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
```

- [ ] **Step 4: 运行测试验证通过**

```bash
cd D:/angent-remind
pytest tests/test_models.py -v
```

预期：全部 PASS

- [ ] **Step 5: 提交**

```bash
cd D:/angent-remind
git add src/models.py tests/test_models.py
git commit -m "feat: add AgentState and StatusType models"
```

---

## Task 3: 配置管理

**文件：**
- Create: `src/config.py`
- Create: `config/default.yaml`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_config.py
import pytest
import tempfile
import os
import yaml
from src.config import Config


def test_load_default_config():
    """测试加载默认配置"""
    config = Config()
    assert config.api_type == "rest"
    assert config.poll_interval == 5
    assert config.window_opacity == 0.9


def test_load_custom_config():
    """测试加载自定义配置"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "type": "websocket",
                "poll_interval": 10
            },
            "window": {
                "opacity": 0.8
            }
        }, f)
        f.flush()

        config = Config(f.name)
        assert config.api_type == "websocket"
        assert config.poll_interval == 10
        assert config.window_opacity == 0.8

        os.unlink(f.name)


def test_config_validation():
    """测试配置验证"""
    config = Config()
    assert config.validate() is True


def test_invalid_poll_interval():
    """测试无效轮询间隔"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "api": {
                "poll_interval": -1
            }
        }, f)
        f.flush()

        config = Config(f.name)
        assert config.validate() is False

        os.unlink(f.name)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_config.py -v
```

预期：FAIL - `ModuleNotFoundError: No module named 'src.config'`

- [ ] **Step 3: 创建默认配置文件**

```yaml
# config/default.yaml
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

- [ ] **Step 4: 编写最小实现**

```python
# src/config.py
import os
from pathlib import Path
from typing import Optional
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

    def validate(self) -> bool:
        """验证配置有效性"""
        if self.poll_interval <= 0:
            return False
        if self.api_timeout <= 0:
            return False
        if not 0 <= self.window_opacity <= 1:
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
git commit -m "feat: add config management with YAML support"
```

---

## Task 4: REST API 轮询器

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

- [ ] **Step 2: 编写失败的测试**

```python
# tests/test_rest_poller.py
import pytest
from unittest.mock import Mock, patch, MagicMock
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

- [ ] **Step 3: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_rest_poller.py -v
```

预期：FAIL - `ModuleNotFoundError`

- [ ] **Step 4: 编写基类**

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

## Task 5: 状态管理器

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


from unittest.mock import Mock
```

- [ ] **Step 3: 运行测试验证失败**

```bash
cd D:/angent-remind
pytest tests/test_state_manager.py -v
```

预期：FAIL - `ModuleNotFoundError`

- [ ] **Step 4: 编写最小实现**

```python
# src/state/manager.py
from typing import Callable, List, Optional
from src.models import AgentState


class StateManager:
    """状态管理器"""

    def __init__(self):
        self._current_state: Optional[AgentState] = None
        self._history: List[AgentState] = []
        self._callbacks: List[Callable[[AgentState], None]] = []
        self._max_history = 1000

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

## Task 6: 悬浮窗基础实现

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

预期：FAIL - `ModuleNotFoundError`

- [ ] **Step 4: 编写最小实现**

```python
# src/ui/floating_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette
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
        status_text = {
            StatusType.RUNNING: "运行中",
            StatusType.COMPLETED: "已完成",
            StatusType.ERROR: "错误",
            StatusType.WAITING: "等待中",
            StatusType.CONFIRM: "需要确认"
        }.get(state.status, "")
        self._status_label.setText(status_text)

        # 更新消息
        self._message_label.setText(state.message[:20] + "..." if len(state.message) > 20 else state.message)

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
git commit -m "feat: add basic floating window with drag support"
```

---

## Task 7: UI 渲染器

**文件：**
- Create: `src/ui/renderer.py`
- Create: `src/ui/system_tray.py`

- [ ] **Step 1: 编写 UI 渲染器**

```python
# src/ui/renderer.py
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
from typing import Optional
import os
from src.models import AgentState, StatusType
from src.ui.floating_window import FloatingWindow
from src.config import Config


class UIRenderer:
    """UI 渲染器"""

    def __init__(self, config: Config):
        self.config = config
        self.floating_window = FloatingWindow()
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self._sound_effects = {}

    def initialize(self):
        """初始化 UI"""
        self._setup_tray()
        self._load_sounds()
        self.floating_window.show()

    def _setup_tray(self):
        """设置系统托盘"""
        from src.ui.system_tray import SystemTray
        self.tray_icon = SystemTray(self.floating_window)
        self.tray_icon.show()

    def _load_sounds(self):
        """加载声音文件"""
        if not self.config.sounds_enabled:
            return

        sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
        for status_type in StatusType:
            sound_file = os.path.join(sounds_dir, f"{status_type.value}.mp3")
            if os.path.exists(sound_file):
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(sound_file))
                effect.setVolume(self.config.sound_volume)
                self._sound_effects[status_type] = effect

    def render(self, state: AgentState):
        """渲染状态"""
        self.floating_window.update_state(state)

        # 播放声音
        if self.config.sounds_enabled:
            self._play_sound(state.status)

    def _play_sound(self, status: StatusType):
        """播放声音"""
        if status in self._sound_effects:
            self._sound_effects[status].play()

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
from PyQt6.QtCore import pyqtSignal
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
        # 使用默认图标
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

## Task 8: 程序入口与主循环

**文件：**
- Create: `src/main.py`

- [ ] **Step 1: 编写主程序**

```python
# src/main.py
import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.config import Config
from src.models import AgentState, StatusType
from src.poller.rest_poller import RestPoller
from src.state.manager import StateManager
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
        self.renderer = UIRenderer(self.config)

        # 初始化轮询器
        self.poller = self._create_poller()

        # 连接信号
        self._connect_signals()

        # 轮询定时器
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)

    def _create_poller(self) -> RestPoller:
        """创建轮询器"""
        return RestPoller(
            url=self.config.api_url,
            interval=self.config.poll_interval,
            timeout=self.config.api_timeout,
            headers=self.config._config.get("api", {}).get("headers", {})
        )

    def _connect_signals(self):
        """连接信号"""
        # 状态变化时更新 UI
        self.state_manager.on_state_change(self.renderer.render)

        # 轮询器状态变化时更新状态管理器
        self.poller.on_status_change(self.state_manager.update_state)

    def _poll(self):
        """执行轮询"""
        state = self.poller.poll()
        if state:
            self.state_manager.update_state(state)

    def run(self):
        """运行程序"""
        # 初始化 UI
        self.renderer.initialize()

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
git commit -m "feat: add main entry point with event loop"
```

---

## Task 9: 集成测试与文档完善

**文件：**
- Modify: `README.md`
- Create: `tests/test_integration.py`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_integration.py
import pytest
from unittest.mock import Mock, patch
from src.models import AgentState, StatusType
from src.state.manager import StateManager
from datetime import datetime


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

- [ ] **Step 2: 运行集成测试**

```bash
cd D:/angent-remind
pytest tests/test_integration.py -v
```

预期：全部 PASS

- [ ] **Step 3: 更新 README.md**

```markdown
# Agent 状态提示软件

AI Agent 状态提示软件，通过悬浮窗实时展示 Agent 运行状态。

## 功能特性

- ✅ 实时监控 Agent 状态（REST API / WebSocket / 文件监听）
- ✅ 悬浮窗展示状态信息
- ✅ 5 种状态类型：运行中、已完成、错误/异常、等待中/空闲、需要确认
- ✅ 支持拖拽、展开详情、右键菜单、声音提醒
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
└── ui/               # 用户界面
```

## 许可证

MIT
```

- [ ] **Step 4: 提交**

```bash
cd D:/angent-remind
git add tests/test_integration.py README.md
git commit -m "docs: add integration tests and update README"
```

---

## 实施计划完成

**计划已完成并保存到：** `docs/superpowers/plans/2026-06-01-agent-status-monitor.md`

**两种执行方式：**

1. **子代理驱动（推荐）** - 每个任务分发一个新的子代理，任务间进行审查，快速迭代

2. **内联执行** - 在当前会话中执行任务，批量执行并设置检查点

**请选择执行方式？**
