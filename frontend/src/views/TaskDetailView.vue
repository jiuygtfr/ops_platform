<template>
  <div class="page-container task-detail">
    <div class="page-header">
        <el-button class="back-btn" @click="$router.back()" circle>
            ←
        </el-button>
        <div class="header-text">
            <h1 class="page-title">{{ task?.name || '任务详情' }}</h1>
            <div class="task-meta" v-if="task">
                <span class="mode-badge">{{ task.mode === 'batch' ? '分批执行' : '广播执行' }}</span>
                <span class="host-count">{{ hostsStatus.length }} 台主机</span>
                <span class="host-count" v-if="task.created_at">执行时间: {{ new Date(task.created_at).toLocaleString() }}</span>
            </div>
        </div>
    </div>

    <div class="detail-grid">
        <div class="status-sidebar">
            <el-card class="content-card status-card">
                <div class="status-summary">
                    <div class="summary-item success">
                        <span class="count">{{ successCount }}</span>
                        <span class="label">成功</span>
                    </div>
                    <div class="summary-item running">
                        <span class="count">{{ runningCount }}</span>
                        <span class="label">执行中</span>
                    </div>
                    <div class="summary-item failed">
                        <span class="count">{{ failedCount }}</span>
                        <span class="label">失败</span>
                    </div>
                </div>
                
                <div class="host-list-status">
                    <div v-for="h in hostsStatus" :key="h.hostId" class="host-status-item">
                        <div class="host-info">
                            <span class="name">{{ getHostName(h.hostId) }}</span>
                        </div>
                        <div class="status-indicator">
                             <el-tag size="small" :type="getStatusType(h.status)" effect="dark" round>
                                 {{ h.status }}
                             </el-tag>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <div class="logs-main">
            <el-card class="content-card logs-card" :body-style="{ padding: '0' }">
                <div class="terminal-header">
                    <span class="dot red"></span>
                    <span class="dot yellow"></span>
                    <span class="dot green"></span>
                    <span class="title">Execution Logs</span>
                </div>
                <div class="logs-container" ref="logsContainer">
                    <div v-for="(log, index) in logs" :key="index" class="log-line">
                        <span class="log-host">[{{ getHostName(log.hostId) }}]</span>
                        <span class="log-content">{{ log.line }}</span>
                    </div>
                    <div v-if="logs.length === 0" class="empty-logs">
                        Waiting for logs...
                    </div>
                </div>
            </el-card>
        </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { getTask } from "@/api/tasks";
import { getHosts, type Host } from "@/api/hosts";

const props = defineProps<{ id: string }>();
const task = ref<any>(null);
const allHosts = ref<Host[]>([]);
const logs = ref<any[]>([]);
const hostsStatus = ref<any[]>([]);
let ws: WebSocket;

const successCount = computed(() => hostsStatus.value.filter(h => h.status === 'success').length);
const runningCount = computed(() => hostsStatus.value.filter(h => h.status === 'running').length);
const failedCount = computed(() => hostsStatus.value.filter(h => h.status === 'failed').length);

const getHostName = (id: number) => {
    const h = allHosts.value.find(x => x.id === id);
    return h ? h.name : `Host-${id}`;
};

const getStatusType = (status: string) => {
    switch(status) {
        case 'success': return 'success';
        case 'failed': return 'danger';
        case 'running': return 'warning';
        default: return 'info';
    }
}

const loadData = async () => {
    allHosts.value = await getHosts();
    task.value = await getTask(parseInt(props.id));
    hostsStatus.value = task.value.hosts.map((h: any) => ({
        hostId: h.host_id,
        status: h.status
    }));
};

const connectWs = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/tasks/${props.id}/stream`;
    
    ws = new WebSocket(wsUrl);
    ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.line) {
            logs.value.push({
                hostId: msg.host_id,
                line: msg.line
            });
            // Auto scroll
            setTimeout(() => {
                const container = document.querySelector('.logs-container');
                if (container) container.scrollTop = container.scrollHeight;
            }, 50);
        }
        if (msg.status) {
            const h = hostsStatus.value.find(x => x.hostId === msg.host_id);
            if (h) {
                h.status = msg.status;
            }
        }
    };
};

onMounted(async () => {
    await loadData();
    connectWs();
});

onBeforeUnmount(() => {
    ws?.close();
});
</script>

<style scoped>
.page-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
}

.back-btn {
    font-size: 18px;
    border: none;
    background: transparent;
}

.page-title {
    font-size: 32px;
    margin: 0;
    line-height: 1.2;
}

.task-meta {
    margin-top: 4px;
    font-size: 14px;
    color: var(--sf-text-secondary);
    display: flex;
    gap: 12px;
    align-items: center;
}

.mode-badge {
    background: #e8e8ed;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
}

.detail-grid {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 24px;
    height: calc(100vh - 180px);
}

.status-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.status-summary {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin-bottom: 24px;
    text-align: center;
}

.summary-item .count {
    display: block;
    font-size: 24px;
    font-weight: 700;
}

.summary-item .label {
    font-size: 12px;
    color: var(--sf-text-secondary);
}

.summary-item.success .count { color: #34c759; }
.summary-item.failed .count { color: #ff3b30; }
.summary-item.running .count { color: #ff9500; }

.host-list-status {
    flex: 1;
    overflow-y: auto;
}

.host-status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
}

.host-status-item:last-child {
    border-bottom: none;
}

.logs-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #1d1d1f !important;
    border: 1px solid #333 !important;
}

.terminal-header {
    padding: 12px 16px;
    background: #2c2c2e;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid #3a3a3c;
}

.dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }

.terminal-header .title {
    margin-left: 12px;
    color: #98989d;
    font-size: 13px;
    font-family: monospace;
}

.logs-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #fff;
}

.log-host {
    color: #0a84ff;
    margin-right: 12px;
    font-weight: bold;
}

.empty-logs {
    color: #666;
    text-align: center;
    margin-top: 40px;
}
</style>
