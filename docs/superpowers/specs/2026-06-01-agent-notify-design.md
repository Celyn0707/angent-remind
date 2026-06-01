# Agent 状态提示软件设计文档（完整版）

**日期：** 2026-06-01
**版本：** 2.0
**状态：** 设计完成，待审核

---

## 1. 概述

### 1.1 项目目标

开发一个 AI Agent 状态提示软件，通过桌面悬浮窗、手机网页、企业微信推送三种方式实时展示 Agent 的运行状态，并支持蓝牙备用连接。

### 1.2 核心功能

- **桌面悬浮窗**：PyQt6 悬浮窗，5种状态类型，支持拖拽、展开详情
- **手机网页**：局域网访问，WebSocket 实时推送，显示详细状态信息
- **企业微信推送**：所有状态变化通过 Webhook 推送通知
- **蓝牙连接**：BLE GATT Server，作为局域网的备用连接方式
- **事件分发**：统一的多通道通知调度

### 1.3 技术选型

- **语言：** Python 3.10+
- **UI 框架：** PyQt6
- **Web 框架：** aiohttp（异步 Web 服务 + WebSocket）
- **蓝牙：** bleak（跨平台 BLE 库）
- **状态来源：** REST API / WebSocket / 文件监听
- **配置格式：** YAML

---

## 2. 系统架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent 状态提示软件                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  API 轮询器  │───▶│  状态管理器  │───▶│  事件分发器  │     │
│  │ (Poller)    │    │ (StateManager)│   │ (Dispatcher)│     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  外部 API   │    │  状态历史   │    │  多通道推送  │     │
│  │ (Agent API) │    │ (History)   │    │ (Notifiers) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                            │               │
│                    ┌───────────────────────┼───────┐       │
│                    │                       │       │       │
│                    ▼                       ▼       ▼       │
│             ┌──────────┐           ┌──────────┐ ┌────────┐│
│             │ PyQt6    │           │  Web     │ │ 企业   ││
│             │ 悬浮窗   │           │  服务    │ │ 微信   ││
│             └──────────┘           └──────────┘ └────────┘│
│                                           │               │
│                                           ▼               │
│                                    ┌──────────┐           │
│                                    │ 手机网页 │           │
│                                    └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 API 轮询器 (Poller)

**职责：** 定时向 Agent API 发送请求，获取当前状态。

**功能：**
- 支持 REST API、WebSocket、文件监听三种模式
- 可配置轮询间隔（默认 5 秒）
- 支持请求超时和重试机制
- 异常处理和降级策略

**接口：**
```python
class BasePoller(ABC):
    def start(self) -> None
    def stop(self) -> None
    def poll(self) -> Optional[AgentState]
    def on_status_change(self, callback: Callable) -> None
```

#### 2.2.2 状态管理器 (StateManager)

**职责：** 管理状态数据，检测状态变化，触发状态转换事件。

**功能：**
- 维护当前状态和状态历史
- 检测状态变化并触发回调（相同状态不重复通知）
- 验证状态数据的合法性
- 支持状态回滚和查询

**接口：**
```python
class StateManager:
    def update_state(self, new_state: AgentState) -> None
    def get_current_state(self) -> Optional[AgentState]
    def get_history(self, limit: int = 100) -> List[AgentState]
    def on_state_change(self, callback: Callable) -> None
```

#### 2.2.3 事件分发器 (Dispatcher)

**职责：** 将状态变化分发到所有已注册的通知通道。

**功能：**
- 管理多个通知通道（Notifier）
- 并发分发到所有通道
- 单个通道失败不影响其他通道
- 支持动态启用/禁用通道

**接口：**
```python
class Dispatcher:
    def register(self, notifier: BaseNotifier) -> None
    def unregister(self, notifier: BaseNotifier) -> None
    def dispatch(self, state: AgentState) -> None
```

#### 2.2.4 通知通道 (Notifiers)

**基类接口：**
```python
class BaseNotifier(ABC):
    async def send(self, state: AgentState) -> bool
    def is_available(self) -> bool
```

**实现：**
- **PyQt6Notifier**：更新悬浮窗 UI
- **WebNotifier**：通过 WebSocket 推送到手机网页
- **WeChatNotifier**：通过 Webhook 推送到企业微信
- **BluetoothNotifier**：通过 BLE Notify 推送到手机

---

## 3. 状态设计

### 3.1 状态类型

| 状态 | 颜色 | 动画 | 图标 | 描述 |
|------|------|------|------|------|
| 运行中 | 🟢 绿色 (#4ade80) | 脉冲效果 | ⚡ | Agent 正在执行任务 |
| 已完成 | 🔵 蓝色 (#60a5fa) | 淡入淡出 | ✅ | 任务执行完成 |
| 错误/异常 | 🔴 红色 (#f87171) | 闪烁提醒 | ❌ | 执行出错或异常 |
| 等待中/空闲 | 🟡 黄色 (#fbbf24) | 缓慢呼吸 | ⏳ | 等待输入或空闲 |
| 需要确认 | 🟣 紫色 (#c084fc) | 弹跳提醒 | ❓ | 需要用户确认操作 |

### 3.2 状态数据结构

```python
@dataclass
class AgentState:
    status: StatusType        # running|completed|error|waiting|confirm
    task: str                 # 当前任务描述
    progress: int             # 进度百分比 (0-100)
    message: str              # 详细信息
    started_at: datetime      # 开始时间
    error: Optional[str]      # 错误信息（仅 error 状态）
    confirm_required: bool    # 是否需要确认
```

### 3.3 状态转换规则

```
空闲 ──▶ 运行中 ──▶ 已完成
  │         │         │
  │         ▼         │
  │      错误/异常 ◀──┘
  │         │
  ▼         ▼
等待中 ◀── 需要确认
```

---

## 4. 通知通道设计

### 4.1 通道优先级

```
状态变化
    │
    ▼
┌───────────────────────────────────────┐
│           事件分发器 (Dispatcher)      │
│  ┌─────────────────────────────────┐  │
│  │  1. PyQt6 悬浮窗 (本地)         │  │
│  │  2. Web 服务 (局域网)           │  │
│  │  3. 企业微信推送 (Webhook)      │  │
│  │  4. 蓝牙通知 (备用)             │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
```

### 4.2 各通道实现

| 通道 | 技术方案 | 连接方式 | 延迟 |
|------|----------|----------|------|
| **PyQt6 悬浮窗** | PyQt6 QWidget | 本地 | 即时 |
| **Web 服务** | aiohttp WebSocket | 局域网 IP:端口 | <100ms |
| **企业微信** | Webhook POST | 互联网 | 1-3s |
| **蓝牙** | BLE GATT Server | 蓝牙配对 | <500ms |

### 4.3 Web 服务架构

```
手机浏览器
    │
    ▼ (WebSocket)
┌───────────────────────────────────┐
│         aiohttp Web 服务          │
│  ┌─────────────┐ ┌─────────────┐ │
│  │  静态文件   │ │  WebSocket  │ │
│  │  (HTML/JS)  │ │   Handler   │ │
│  └─────────────┘ └─────────────┘ │
│              │                   │
│              ▼                   │
│       ┌─────────────┐            │
│       │ 状态管理器  │            │
│       └─────────────┘            │
└───────────────────────────────────┘
```

**手机网页功能：**
- 实时状态图标和颜色
- 任务名称和进度条
- 详细消息
- 运行时间
- 状态历史列表（最近 20 条）

### 4.4 企业微信推送

**Webhook 格式：**
```json
{
  "msgtype": "markdown",
  "markdown": {
    "content": "## Agent 状态更新\n\n> **状态：** 运行中 ⚡\n> **任务：** 分析代码结构\n> **进度：** 65%\n> **消息：** 正在处理第3个文件\n\n[查看详情](http://192.168.1.100:8080)"
  }
}
```

### 4.5 蓝牙连接

**角色：**
- 电脑端：BLE Peripheral（GATT Server）
- 手机端：BLE Central（GATT Client）

**GATT 服务设计：**

| Service | Characteristic | 权限 | 用途 |
|---------|---------------|------|------|
| Agent Status | Status Type | Read/Notify | 状态类型 |
| Agent Status | Task Name | Read | 当前任务名 |
| Agent Status | Progress | Read/Notify | 进度百分比 |
| Agent Status | Message | Read | 详细消息 |
| Agent Status | Timestamp | Read | 更新时间 |

**连接流程：**
1. 电脑启动 BLE GATT Server
2. 手机 App/浏览器扫描并连接
3. 手机订阅 Status 和 Progress 的 Notify
4. 状态变化时，电脑通过 Notify 推送更新
5. 断开连接时，回退到企业微信推送

**技术选型：**
- BLE Server：`bleak`（Python 跨平台 BLE 库）
- 手机端：Web Bluetooth API（Chrome/Edge 支持，iOS 不支持）

---

## 5. 界面设计

### 5.1 桌面悬浮窗

#### 紧凑模式（默认）

```
┌─────────────────────┐
│ ⚡ 运行中            │
│ 正在处理请求...      │
│ 点击查看详情         │
└─────────────────────┘
```

- 尺寸：200px × 80px
- 位置：默认右下角，可拖拽
- 透明度：90%
- 置顶显示

#### 展开模式（双击后）

```
┌─────────────────────────────┐
│ ⚡ 运行中                    │
│ 当前任务：分析代码结构       │
│ 已运行：2 分 30 秒           │
│ 进度：65% [████████░░░]     │
└─────────────────────────────┘
```

- 尺寸：300px × 200px
- 显示详细任务信息
- 显示进度条

### 5.2 手机网页

```
┌─────────────────────────────┐
│     Agent 状态监控          │
├─────────────────────────────┤
│                             │
│         ⚡ 运行中           │
│                             │
│    ████████████░░░░ 65%    │
│                             │
│  任务：分析代码结构         │
│  消息：正在处理第3个文件    │
│  已运行：2 分 30 秒         │
│                             │
├─────────────────────────────┤
│  最近状态                   │
│  ─────────────────────────  │
│  ✅ 完成 - 代码审查         │
│  ❌ 错误 - 连接超时         │
│  ⚡ 运行 - 数据分析         │
│  ...                        │
└─────────────────────────────┘
```

### 5.3 系统托盘

- 状态图标（与当前状态颜色匹配）
- 右键菜单：
  - 显示/隐藏悬浮窗
  - 查看历史记录
  - 设置
  - 退出

---

## 6. 配置设计

### 6.1 配置文件

**路径：** `~/.agent-monitor/config.yaml`

**完整示例：**
```yaml
# API 配置
api:
  type: rest                    # rest | websocket | file
  url: http://localhost:8080/api/agent/status
  method: GET
  headers:
    Authorization: "Bearer your-token-here"
  poll_interval: 5              # 轮询间隔（秒）
  timeout: 10                   # 请求超时（秒）
  retry_count: 3                # 重试次数

# 悬浮窗配置
window:
  position: bottom-right        # 默认位置
  opacity: 0.9                  # 透明度 (0.0-1.0)
  always_on_top: true           # 置顶显示
  click_to_expand: true         # 点击展开详情
  drag_enabled: true            # 允许拖拽
  snap_to_edge: true            # 吸附屏幕边缘

# 通知配置
notifications:
  # 企业微信
  wechat:
    enabled: true
    webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
    push_on: ["running", "completed", "error", "waiting", "confirm"]
  
  # Web 服务
  web:
    enabled: true
    port: 8080
    host: "0.0.0.0"
  
  # 蓝牙
  bluetooth:
    enabled: false
    device_name: "Agent Monitor"
    auto_reconnect: true

# 状态颜色配置
colors:
  running: "#4ade80"
  completed: "#60a5fa"
  error: "#f87171"
  waiting: "#fbbf24"
  confirm: "#c084fc"

# 声音配置
sounds:
  enabled: true
  volume: 0.7
  on_running: "sounds/running.mp3"
  on_completed: "sounds/completed.mp3"
  on_error: "sounds/error.mp3"
  on_waiting: "sounds/waiting.mp3"
  on_confirm: "sounds/confirm.mp3"

# 日志配置
logging:
  enabled: true
  level: INFO
  file: logs/agent-monitor.log
  max_size: 10MB
  backup_count: 5
```

---

## 7. 目录结构

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
│   └── default.yaml            # 默认配置
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_config.py
│   ├── test_rest_poller.py
│   ├── test_state_manager.py
│   ├── test_dispatcher.py
│   ├── test_wechat.py
│   ├── test_web_server.py
│   └── test_floating_window.py
├── requirements.txt
└── README.md
```

---

## 8. 依赖项

### 8.1 核心依赖

```
PyQt6>=6.5.0
PyQt6-Qt6>=6.5.0
PyQt6-sip>=13.5.0
requests>=2.31.0
websockets>=12.0
aiohttp>=3.9.0
bleak>=0.21.0
pyyaml>=6.0
watchdog>=3.0.0
```

### 8.2 开发依赖

```
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-aiohttp>=1.0.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.0
```

---

## 9. 错误处理

### 9.1 API 连接异常

- **网络超时：** 重试 3 次，间隔递增（1s, 2s, 4s）
- **连接拒绝：** 显示错误状态，每 30 秒重试
- **认证失败：** 显示错误提示，停止轮询

### 9.2 通知通道异常

- **企业微信推送失败：** 静默失败，记录日志，不影响其他通道
- **Web 服务端口占用：** 自动尝试下一个端口（8081, 8082...）
- **蓝牙连接断开：** 自动重连 3 次，失败后回退到企业微信
- **手机网页断开：** WebSocket 自动重连，显示连接状态

### 9.3 状态数据异常

- **格式错误：** 记录日志，使用上一次有效状态
- **字段缺失：** 使用默认值填充
- **状态非法：** 忽略该状态更新

---

## 10. 测试策略

### 10.1 单元测试

- 状态管理器的状态转换逻辑
- API 轮询器的请求和解析
- 配置文件的加载和验证
- 各通知通道的发送逻辑

### 10.2 集成测试

- 完整的状态更新流程：Poller → StateManager → Dispatcher → Notifiers
- 多种 API 类型的兼容性
- 配置变更的生效验证

### 10.3 UI 测试

- 悬浮窗的显示和隐藏
- 拖拽和位置记忆
- 状态动画效果
- 声音播放

### 10.4 Web 测试

- WebSocket 连接和断开
- 消息推送和接收
- 静态文件服务

---

## 11. 后续扩展

### 11.1 功能扩展

- 支持多 Agent 监控
- 状态历史查看界面
- 状态统计和分析
- 自定义状态类型
- 插件系统

### 11.2 平台扩展

- macOS 原生支持
- Linux 原生支持
- iOS App（Web Bluetooth 不支持 iOS）

---

## 12. 审核清单

- [x] 架构设计完整
- [x] 状态类型定义清晰
- [x] 通知通道设计明确
- [x] 蓝牙连接方案可行
- [x] 界面设计合理
- [x] API 接口明确
- [x] 配置设计完善
- [x] 错误处理完备
- [x] 测试策略明确
- [x] 目录结构清晰
- [x] 依赖项列出

---

**文档完成时间：** 2026-06-01
**下一步：** 用户审核设计文档，确认后进入实施规划阶段
