# Agent 状态提示软件设计文档

**日期：** 2026-06-01
**版本：** 1.0
**状态：** 设计完成，待审核

---

## 1. 概述

### 1.1 项目目标

开发一个 AI Agent 状态提示软件，通过悬浮窗实时展示 Agent 的运行状态，帮助用户及时了解 Agent 的工作进展。

### 1.2 核心功能

- 实时监控 Agent 状态（通过 API 接口）
- 悬浮窗展示状态信息
- 5 种状态类型：运行中、已完成、错误/异常、等待中/空闲、需要确认
- 丰富的交互功能：拖拽、展开详情、右键菜单、声音提醒
- 可配置的视觉和行为参数

### 1.3 技术选型

- **语言：** Python 3.10+
- **UI 框架：** PyQt6
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
│  │  API 轮询器  │───▶│  状态管理器  │───▶│  UI 渲染器   │     │
│  │ (Poller)    │    │ (StateManager)│   │ (Renderer)  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  外部 API   │    │  状态历史   │    │  悬浮窗/托盘  │     │
│  │ (Agent API) │    │ (History)   │    │ (FloatingWindow)│   │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

数据流：
Agent API ──▶ Poller ──▶ StateManager ──▶ Renderer ──▶ 悬浮窗显示
                              │
                              ▼
                         状态历史记录
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
class Poller:
    def start(self) -> None
    def stop(self) -> None
    def on_status_change(self, callback: Callable) -> None
```

#### 2.2.2 状态管理器 (StateManager)

**职责：** 管理状态数据，检测状态变化，触发状态转换事件。

**功能：**
- 维护当前状态和状态历史
- 检测状态变化并触发回调
- 验证状态数据的合法性
- 支持状态回滚和查询

**接口：**
```python
class StateManager:
    def update_state(self, new_state: AgentState) -> None
    def get_current_state(self) -> AgentState
    def get_history(self, limit: int = 100) -> List[AgentState]
    def on_state_change(self, callback: Callable) -> None
```

#### 2.2.3 UI 渲染器 (Renderer)

**职责：** 负责悬浮窗、系统托盘的渲染，处理动画效果、声音播放、用户交互。

**功能：**
- 渲染悬浮窗界面
- 处理状态动画效果
- 播放声音提醒
- 管理用户交互事件

**接口：**
```python
class Renderer:
    def render(self, state: AgentState) -> None
    def show_notification(self, message: str) -> None
    def play_sound(self, sound_type: str) -> None
```

#### 2.2.4 悬浮窗 (FloatingWindow)

**职责：** 主要的状态展示界面，支持拖拽、展开详情、右键菜单、状态视觉区分。

**功能：**
- 显示当前状态图标和简要信息
- 点击展开详情面板
- 支持拖拽移动和边缘吸附
- 右键显示上下文菜单
- 状态颜色和动画区分

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
    status: str                    # running|completed|error|waiting|confirm
    task: str                      # 当前任务描述
    progress: int                  # 进度百分比 (0-100)
    message: str                   # 详细信息
    started_at: datetime           # 开始时间
    error: Optional[str]           # 错误信息（仅 error 状态）
    confirm_required: bool         # 是否需要确认
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

**合法转换：**
- 空闲 → 运行中、等待中
- 运行中 → 已完成、错误/异常、需要确认
- 已完成 → 空闲、运行中
- 错误/异常 → 空闲、运行中
- 等待中 → 运行中、空闲
- 需要确认 → 运行中、空闲

---

## 4. 界面设计

### 4.1 悬浮窗布局

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

#### 展开模式（点击后）

```
┌─────────────────────────────┐
│ ⚡ 运行中                    │
│ 当前任务：分析代码结构       │
│ 已运行：2 分 30 秒           │
│ 进度：65% [████████░░░]     │
│ [暂停] [取消]               │
└─────────────────────────────┘
```

- 尺寸：300px × 200px
- 显示详细任务信息
- 显示进度条
- 显示操作按钮

### 4.2 系统托盘

- 状态图标（与当前状态颜色匹配）
- 右键菜单：
  - 显示/隐藏悬浮窗
  - 查看历史记录
  - 设置
  - 退出

### 4.3 交互功能

1. **拖拽移动**
   - 鼠标按住悬浮窗可自由拖拽
   - 松开后自动吸附屏幕边缘
   - 记住上次位置

2. **点击展开**
   - 点击悬浮窗展开详情面板
   - 再次点击收起
   - 点击外部区域自动收起

3. **右键菜单**
   - 显示/隐藏悬浮窗
   - 暂停/恢复监控
   - 查看历史记录
   - 打开设置
   - 退出程序

4. **声音提醒**
   - 状态变化时播放提示音
   - 错误和需要确认时音量更大
   - 可配置开关和音量

---

## 5. API 接口设计

### 5.1 REST API

**请求：**
```http
GET http://localhost:8080/api/agent/status
Authorization: Bearer <token>
```

**响应：**
```json
{
  "status": "running",
  "task": "分析代码结构",
  "progress": 65,
  "message": "正在处理第3个文件",
  "started_at": "2026-06-01T10:30:00Z",
  "error": null,
  "confirm_required": false
}
```

### 5.2 WebSocket

**连接：**
```
ws://localhost:8080/ws/agent/status
```

**消息格式：**
```json
{
  "type": "status_update",
  "data": {
    "status": "running",
    "task": "分析代码结构",
    "progress": 65,
    "message": "正在处理第3个文件",
    "started_at": "2026-06-01T10:30:00Z",
    "error": null,
    "confirm_required": false
  }
}
```

### 5.3 文件监听

**状态文件路径：** 可配置（默认 `~/.agent/status.json`）

**文件格式：**
```json
{
  "status": "running",
  "task": "分析代码结构",
  "progress": 65,
  "message": "正在处理第3个文件",
  "started_at": "2026-06-01T10:30:00Z",
  "error": null,
  "confirm_required": false
}
```

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
  position: bottom-right        # 默认位置：top-left, top-right, bottom-left, bottom-right
  opacity: 0.9                  # 透明度 (0.0-1.0)
  always_on_top: true           # 置顶显示
  click_to_expand: true         # 点击展开详情
  drag_enabled: true            # 允许拖拽
  snap_to_edge: true            # 吸附屏幕边缘

# 状态颜色配置
colors:
  running: "#4ade80"            # 绿色
  completed: "#60a5fa"          # 蓝色
  error: "#f87171"              # 红色
  waiting: "#fbbf24"            # 黄色
  confirm: "#c084fc"            # 紫色

# 声音配置
sounds:
  enabled: true
  volume: 0.7                   # 音量 (0.0-1.0)
  on_running: "sounds/running.mp3"
  on_completed: "sounds/completed.mp3"
  on_error: "sounds/error.mp3"
  on_waiting: "sounds/waiting.mp3"
  on_confirm: "sounds/confirm.mp3"

# 日志配置
logging:
  enabled: true
  level: INFO                   # DEBUG, INFO, WARNING, ERROR
  file: logs/agent-monitor.log
  max_size: 10MB
  backup_count: 5
```

---

## 7. 目录结构

```
angent-remind/
├── src/
│   ├── main.py                 # 程序入口
│   ├── config.py               # 配置管理
│   ├── poller/
│   │   ├── __init__.py
│   │   ├── base.py             # 轮询器基类
│   │   ├── rest_poller.py      # REST API 轮询器
│   │   ├── ws_poller.py        # WebSocket 轮询器
│   │   └── file_poller.py      # 文件监听轮询器
│   ├── state/
│   │   ├── __init__.py
│   │   ├── manager.py          # 状态管理器
│   │   └── models.py           # 状态数据模型
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── floating_window.py  # 悬浮窗
│   │   ├── system_tray.py      # 系统托盘
│   │   ├── renderer.py         # UI 渲染器
│   │   └── sounds/             # 声音文件
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       └── helpers.py          # 辅助函数
├── config/
│   └── config.yaml             # 默认配置
├── tests/
│   ├── test_poller.py
│   ├── test_state.py
│   └── test_ui.py
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-06-01-agent-status-monitor-design.md
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
pyyaml>=6.0
watchdog>=3.0.0
```

### 8.2 开发依赖

```
pytest>=7.4.0
pytest-qt>=4.2.0
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

### 9.2 状态数据异常

- **格式错误：** 记录日志，使用上一次有效状态
- **字段缺失：** 使用默认值填充
- **状态非法：** 忽略该状态更新

### 9.3 UI 异常

- **渲染错误：** 降级到简单文本显示
- **声音播放失败：** 静默忽略，记录日志
- **托盘图标异常：** 仅使用悬浮窗模式

---

## 10. 测试策略

### 10.1 单元测试

- 状态管理器的状态转换逻辑
- API 轮询器的请求和解析
- 配置文件的加载和验证

### 10.2 集成测试

- 完整的状态更新流程
- 多种 API 类型的兼容性
- 配置变更的生效验证

### 10.3 UI 测试

- 悬浮窗的显示和隐藏
- 拖拽和位置记忆
- 状态动画效果
- 声音播放

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
- 移动端通知推送

---

## 12. 审核清单

- [x] 架构设计完整
- [x] 状态类型定义清晰
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
