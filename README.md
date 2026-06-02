# Agent 状态提示软件 (Agent Monitor)

AI Agent 状态提示软件，通过悬浮窗实时展示 Agent 运行状态，支持多种通知方式（企业微信、Web 服务、蓝牙），可方便地在桌面和手机上监控 Agent 的工作进度。

## 功能特性

### 状态监控
- 通过 REST API 轮询获取 Agent 实时状态
- 支持 WebSocket 实时推送
- 支持文件监听获取状态变化

### 5 种状态类型

| 状态 | 说明 | 颜色 |
|------|------|------|
| `running` | 运行中 | 绿色 `#4ade80` |
| `completed` | 已完成 | 蓝色 `#60a5fa` |
| `error` | 错误/异常 | 红色 `#f87171` |
| `waiting` | 等待中/空闲 | 黄色 `#fbbf24` |
| `confirm` | 需要确认 | 紫色 `#c084fc` |

### 悬浮窗 UI
- 桌面悬浮窗实时展示 Agent 状态信息
- 支持拖拽移动位置
- 点击展开查看详细信息
- 右键菜单操作
- 自动吸附屏幕边缘
- 系统托盘图标

### 通知方式
- **企业微信通知** - 通过 Webhook 推送状态到企业微信群
- **Web 服务** - 内置 HTTP 服务，支持 REST API 和 WebSocket，方便手机访问
- **蓝牙通知** - 通过 BLE 蓝牙广播状态信息

### 声音提醒
- 状态变化时播放提示音
- 支持自定义音量

## 安装

### 环境要求

- Python 3.10+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 依赖列表

| 包名 | 用途 |
|------|------|
| PyQt6 | 桌面 UI 框架 |
| requests | REST API 轮询 |
| websockets | WebSocket 连接 |
| aiohttp | Web 服务与异步 HTTP |
| bleak | 蓝牙 BLE 支持 |
| pyyaml | YAML 配置解析 |
| watchdog | 文件监听 |

## 使用

```bash
# 使用默认配置（悬浮窗模式）
python -m src.main

# 指定配置文件
python -m src.main -c path/to/config.yaml

# 显示管理控制台
python -m src.main --gui
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-c`, `--config` | 指定配置文件路径 |
| `--gui` | 启动管理控制台（GUI 模式） |

## 管理控制台

管理控制台提供图形化界面，包含以下功能：

- **配置管理**：图形化编辑 API、界面、声音、日志等配置
- **状态监控**：实时显示 Agent 状态、任务信息、运行时间、历史记录
- **通知管理**：管理企业微信、手机网页、蓝牙、桌面悬浮窗等通知通道
- **日志查看**：查看运行日志、错误日志、状态变化日志、通知日志

启动管理控制台：
```bash
python -m src.main --gui
```

## 配置

### 配置文件位置

- 默认配置：`config/default.yaml`
- 用户配置：`~/.agent-monitor/config.yaml`（会与默认配置合并）

### 配置示例

```yaml
# Agent 状态 API 配置
api:
  type: rest                        # 轮询类型：rest
  url: http://localhost:8080/api/agent/status  # API 地址
  method: GET                       # 请求方法
  headers: {}                       # 自定义请求头
  poll_interval: 5                  # 轮询间隔（秒）
  timeout: 10                       # 请求超时（秒）
  retry_count: 3                    # 重试次数

# 悬浮窗配置
window:
  position: bottom-right            # 初始位置：bottom-right, bottom-left, top-right, top-left
  opacity: 0.9                      # 窗口透明度（0.0-1.0）
  always_on_top: true               # 置顶显示
  click_to_expand: true             # 点击展开详情
  drag_enabled: true                # 启用拖拽
  snap_to_edge: true                # 吸附屏幕边缘

# 通知配置
notifications:
  # 企业微信通知
  wechat:
    enabled: true
    webhook: ""                     # 企业微信 Webhook 地址
    push_on:                        # 哪些状态触发推送
      - running
      - completed
      - error
      - waiting
      - confirm

  # Web 服务（用于手机访问）
  web:
    enabled: true
    port: 8080                      # 服务端口
    host: "0.0.0.0"                 # 监听地址

  # 蓝牙通知
  bluetooth:
    enabled: false
    device_name: "Agent Monitor"    # 蓝牙设备名称
    auto_reconnect: true            # 自动重连

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
  volume: 0.7                       # 音量（0.0-1.0）

# 日志配置
logging:
  enabled: true
  level: INFO                       # 日志级别
  file: logs/agent-monitor.log      # 日志文件路径
  max_size: 10MB                    # 单个日志文件最大大小
  backup_count: 5                   # 日志备份数量
```

## 状态说明

程序通过轮询 Agent 提供的 REST API 获取状态数据。API 需返回如下 JSON 格式：

```json
{
  "status": "running",
  "task": "正在处理数据",
  "progress": 65,
  "message": "正在处理第 3/5 批数据...",
  "started_at": "2026-06-01T10:30:00",
  "error": null,
  "confirm_required": false
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态类型：`running` / `completed` / `error` / `waiting` / `confirm` |
| `task` | string | 当前任务描述 |
| `progress` | int | 进度百分比（0-100） |
| `message` | string | 状态消息 |
| `started_at` | string | 任务开始时间（ISO 8601） |
| `error` | string | 错误信息（仅 `error` 状态） |
| `confirm_required` | bool | 是否需要用户确认（仅 `confirm` 状态） |

## 手机访问

程序内置 Web 服务，可以通过手机浏览器实时查看 Agent 状态：

1. 确保手机和电脑在同一局域网
2. 启动程序后，在手机浏览器中访问：`http://<电脑IP>:8080`
3. Web 服务提供：
   - **REST API**: `GET /api/status` - 获取当前状态
   - **WebSocket**: `ws://<电脑IP>:8080/ws` - 实时状态推送
   - **首页**: `/` - 状态查看页面

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行并显示覆盖率
pytest --cov=src
```

### 测试依赖

- pytest
- pytest-qt (UI 测试)
- pytest-asyncio (异步测试)
- pytest-aiohttp (Web 服务测试)

## 目录结构

```
agent-monitor/
├── config/
│   └── default.yaml          # 默认配置文件
├── src/
│   ├── __init__.py
│   ├── main.py               # 程序入口
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型（AgentState, StatusType）
│   ├── poller/
│   │   ├── __init__.py
│   │   ├── base.py           # 轮询器基类
│   │   └── rest_poller.py    # REST API 轮询器
│   ├── state/
│   │   ├── __init__.py
│   │   └── manager.py        # 状态管理器
│   ├── notifier/
│   │   ├── __init__.py
│   │   ├── base.py           # 通知器基类
│   │   ├── dispatcher.py     # 通知分发器
│   │   ├── wechat.py         # 企业微信通知
│   │   ├── web_server.py     # Web 服务通知
│   │   └── bluetooth.py      # 蓝牙通知
│   └── ui/
│       ├── __init__.py
│       ├── floating_window.py # 悬浮窗
│       ├── renderer.py       # UI 渲染器
│       ├── system_tray.py    # 系统托盘
│       ├── gui_control_panel.py    # 管理控制台
│       ├── config_tab.py     # 配置管理标签页
│       ├── status_tab.py     # 状态监控标签页
│       ├── notification_tab.py # 通知管理标签页
│       └── log_tab.py        # 日志查看标签页
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # 数据模型测试
│   ├── test_config.py        # 配置管理测试
│   ├── test_rest_poller.py   # REST 轮询器测试
│   ├── test_state_manager.py # 状态管理器测试
│   ├── test_dispatcher.py    # 通知分发器测试
│   ├── test_wechat.py        # 企业微信通知测试
│   ├── test_web_server.py    # Web 服务测试
│   ├── test_bluetooth.py     # 蓝牙通知测试
│   ├── test_floating_window.py # 悬浮窗测试
│   └── test_integration.py   # 集成测试
├── requirements.txt          # Python 依赖
├── README.md                 # 项目说明
└── .gitignore
```

## 许可证

MIT License
