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