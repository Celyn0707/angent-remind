class AgentMonitor {
    static STATUS_ICONS = {
        running: '⚡',
        completed: '✅',
        error: '❌',
        waiting: '⏳',
        confirm: '❓'
    };

    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.history = [];
        this.maxHistory = 20;
        this.runtimeInterval = null;
        this.startedAt = null;

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
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'status_update') {
                    this.updateStatus(data.data);
                }
            } catch (e) {
                console.error('解析消息失败:', e, event.data);
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
        const statusTexts = {
            running: '运行中',
            completed: '已完成',
            error: '错误',
            waiting: '等待中',
            confirm: '需要确认'
        };

        document.getElementById('status-icon').textContent = AgentMonitor.STATUS_ICONS[state.status] || '?';
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
        const historyItem = {
            icon: AgentMonitor.STATUS_ICONS[state.status] || '?',
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
        historyList.innerHTML = '';
        for (const item of this.history) {
            const row = document.createElement('div');
            row.className = 'history-item';

            const iconSpan = document.createElement('span');
            iconSpan.className = 'history-icon';
            iconSpan.textContent = item.icon;

            const content = document.createElement('div');
            content.className = 'history-content';

            const taskDiv = document.createElement('div');
            taskDiv.className = 'history-task';
            taskDiv.textContent = item.task;

            const timeDiv = document.createElement('div');
            timeDiv.className = 'history-time';
            timeDiv.textContent = item.time;

            content.appendChild(taskDiv);
            content.appendChild(timeDiv);
            row.appendChild(iconSpan);
            row.appendChild(content);
            historyList.appendChild(row);
        }
    }

    updateRuntime() {
        this.clearRuntime();
        this.runtimeInterval = setInterval(() => {
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

    clearRuntime() {
        if (this.runtimeInterval) {
            clearInterval(this.runtimeInterval);
            this.runtimeInterval = null;
        }
    }
}

// 启动应用
const monitor = new AgentMonitor();
